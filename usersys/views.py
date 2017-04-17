#coding=utf-8
import traceback

import datetime
from django.contrib import auth
from django.core.exceptions import FieldDoesNotExist
from django.core.paginator import Paginator, EmptyPage
from django.db import transaction,models

# Create your views here.
from django.db.models import Q
from django.db.models.fields.reverse_related import ForeignObjectRel
from guardian.shortcuts import assign_perm
from rest_framework import filters
from rest_framework import status
from rest_framework import viewsets

from rest_framework.decorators import api_view, detail_route, list_route
from usersys.models import MyUser, MyToken, UserRelation, userTags, MobileAuthCode , InvestError
from usersys.serializer import UserSerializer, UserListSerializer, UserRelationSerializer,\
    CreatUserSerializer , UserCommenSerializer
from sourcetype.models import Tag
from utils import perimissionfields
from utils.util import read_from_cache, write_to_cache, loginTokenIsAvailable, JSONResponse,\
    catchexcption, cache_delete_key, maketoken


class UserView(viewsets.ModelViewSet):
    filter_backends = (filters.DjangoFilterBackend,)
    queryset = MyUser.objects.filter(is_deleted=False)
    filter_fields = ('mobile','email','name','id','groups')
    serializer_class = UserSerializer
    redis_key = 'users'
    Model = MyUser

    def get_object(self,pk=None):
        if pk:
            obj = read_from_cache(self.redis_key + '_%s' % pk)
            if not obj:
                try:
                    obj = self.Model.objects.get(id=pk, is_deleted=False)
                except self.Model.DoesNotExist:
                    raise InvestError(code=2002)
                else:
                    write_to_cache(self.redis_key + '_%s' % pk, obj)
        else:
            lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
            assert lookup_url_kwarg in self.kwargs, (
                'Expected view %s to be called with a URL keyword argument '
                'named "%s". Fix your URL conf, or set the `.lookup_field` '
                'attribute on the view correctly.' %
                (self.__class__.__name__, lookup_url_kwarg)
            )
            obj = read_from_cache(self.redis_key+'_%s'%self.kwargs[lookup_url_kwarg])
            if not obj:
                try:
                    obj = self.Model.objects.get(id=self.kwargs[lookup_url_kwarg],is_deleted=False)
                except self.Model.DoesNotExist:
                    raise InvestError(code=2002)
                else:
                    write_to_cache(self.redis_key+'_%s'%self.kwargs[lookup_url_kwarg],obj)
        return obj

    @loginTokenIsAvailable(['usersys.admin_getuser','usersys.user_getuser'])
    def list(self, request, *args, **kwargs):
        page_size = request.GET.get('page_size')
        page_index = request.GET.get('page_index')  #从第一页开始
        if not page_size:
            page_size = 10
        if not page_index:
            page_index = 1
        queryset = self.filter_queryset(self.queryset)
        try:
            queryset = Paginator(queryset, page_size)
        except EmptyPage:
            return JSONResponse({'success':True,'result':[],'errorcode':1000,'errormsg':None})
        queryset = queryset.page(page_index)
        serializer = UserListSerializer(queryset, many=True)
        return JSONResponse({'success':True,'result': serializer.data,'errorcode':1000,'errormsg':None})

    #注册用户(新注册用户没有交易师)
    def create(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                data = request.data
                mobilecode = data.pop('mobilecode', None)
                mobilecodetoken = data.pop('mobilecodetoken', None)
                mobile = data.get('mobile')
                email = data.get('email')
                if mobile:
                    try:
                        mobileauthcode = MobileAuthCode.objects.get(mobile=mobile, code=mobilecode, token=mobilecodetoken)
                    except MobileAuthCode.DoesNotExist:
                        raise InvestError(code=2005)
                    else:
                        if mobileauthcode.isexpired():
                            raise InvestError(code=20051)
                    if email:
                        filterQ = Q(mobile=mobile) | Q(email=email)
                    else:
                        filterQ = Q(mobile=mobile)
                elif email:
                    filterQ = Q(email=email)
                else:
                    raise InvestError(code=2007,msg='mobile、email不能都为空')
                try:
                    self.queryset.get(filterQ)
                except MyUser.DoesNotExist:
                    pass
                else:
                    raise InvestError(code=2004)
                user = MyUser(email=email,mobile=mobile)
                password = data.pop('password', None)
                user.set_password(password)
                user.save()
                tags = data.pop('tags', None)
                userserializer = CreatUserSerializer(user, data=data)
                if userserializer.is_valid():
                    user = userserializer.save()
                    if tags:
                        usertaglist = []
                        for tag in tags:
                            usertaglist.append(userTags(user=user, tag_id=tag, ))
                        user.user_tags.bulk_create(usertaglist)
                else:
                    raise InvestError(code=20071,msg='%s\n%s' % (userserializer.error_messages, userserializer.errors))
                return JSONResponse({'success': True, 'result': UserSerializer(user).data, 'errorcode':1000,'errormsg':None})
        except InvestError as err:
            return JSONResponse({'success': False, 'result': None, 'errorcode':err.code,'errormsg':err.msg})
        except Exception:
            catchexcption(request)
            return JSONResponse({'success': False, 'result': None,'errorcode':9999, 'errormsg': traceback.format_exc().split('\n')[-2]})

    # 新增用户
    @loginTokenIsAvailable()
    def adduser(self, request, *args, **kwargs):
        data = request.data
        data['createduser'] = request.user.id
        data['createdtime'] = datetime.datetime.now()
        if request.user.has_perm('usersys.admin_adduser'):
            canCreateField = perimissionfields.userpermfield['usersys.admin_adduser']
        elif request.user.has_perm('usersys.user_adduser'):
            canCreateField = perimissionfields.userpermfield['usersys.trader_adduser']
        else:
            return JSONResponse({'result': None, 'success': False, 'errorcode':2009,'errormsg':None})
        try:
            with transaction.atomic():
                password = data.pop('password','Aa123456')
                email = data.get('email')
                mobile = data.get('mobile')
                try:
                    user = self.get_queryset().get(Q(mobile=mobile) | Q(email=email))
                except MyUser.DoesNotExist:
                    pass
                else:
                    raise InvestError(code=2004)
                user = MyUser()
                user.set_password(password)
                user.save()
                keylist = data.keys()
                cannoteditlist = [key for key in keylist if key not in canCreateField]
                if cannoteditlist:
                    raise InvestError(code=2009,msg='没有权限修改%s' % cannoteditlist)
                tags = data.pop('tags', None)
                userserializer = CreatUserSerializer(user, data=data)
                if userserializer.is_valid():
                    user = userserializer.save()
                    if tags:
                        usertaglist = []
                        for tag in tags:
                            usertaglist.append(userTags(user=user, tag_id=tag, ))
                        user.user_tags.bulk_create(usertaglist)
                else:
                    raise InvestError(code=20071,msg='userdata有误_%s\n%s' % (userserializer.error_messages, userserializer.errors))
                if user.createuser:
                    assign_perm('usersys.user_getuser', user.createuser, user)
                    assign_perm('usersys.user_changeuser', user.createuser, user)
                    assign_perm('usersys.user_deleteuser', user.createuser, user)
                return JSONResponse({'success': True, 'result': UserSerializer(user).data, 'errorcode': 1000,'errormsg':None})
        except InvestError as err:
            return JSONResponse({'success': False, 'result': None, 'errorcode': err.code, 'errormsg': err.msg})
        except Exception:
            catchexcption(request)
            return JSONResponse({'success': False, 'result': None, 'errorcode': 9999,
                                 'errormsg': traceback.format_exc().split('\n')[-2]})

    #get
    @loginTokenIsAvailable()
    def retrieve(self, request, *args, **kwargs):
        try:
            user = self.get_object()
            if request.user == user:
                userserializer = UserListSerializer
            else:
                if request.user.has_perm('usersys.admin_getuser'):
                    userserializer = UserListSerializer
                elif request.user.has_perm('usersys.user_getuser'):
                    userserializer = UserListSerializer
                elif request.user.has_perm('usersys.user_getuser',user):
                    userserializer = UserListSerializer
                else:
                    raise InvestError(code=2009)
            serializer = userserializer(user)
            return JSONResponse({'success':True,'result': serializer.data,'errorcode':1000,'errormsg':None})
        except InvestError as err:
            return JSONResponse({'success': False, 'result': None, 'errorcode': err.code, 'errormsg': err.msg})
        except Exception:
            catchexcption(request)
            return JSONResponse({'success': False, 'result': None, 'errorcode': 9999,'errormsg': traceback.format_exc().split('\n')[-2]})

    @detail_route(methods=['get'])
    @loginTokenIsAvailable()
    def getdetailinfo(self, request, *args, **kwargs):
        try:
            user = self.get_object()
            if request.user == user:
                userserializer = UserSerializer
            else:
                if request.user.has_perm('usersys.admin_getuser'):
                    userserializer = UserSerializer
                elif request.user.has_perm('usersys.user_getuser'):
                    userserializer = UserListSerializer
                elif request.user.has_perm('usersys.user_getuser', user):
                    userserializer = UserSerializer
                else:
                    raise InvestError(code=2009)
            serializer = userserializer(user)
            response = {'success': True, 'result': serializer.data, 'errorcode':1000,'errormsg':None}
            return JSONResponse(response)
        except InvestError as err:
            return JSONResponse({'success': False, 'result': None, 'errorcode': err.code, 'errormsg': err.msg})
        except Exception:
            catchexcption(request)
            return JSONResponse({'success': False, 'result': None, 'errorcode': 9999,
                                 'errormsg': traceback.format_exc().split('\n')[-2]})

    #put
    # @loginTokenIsAvailable()
    def update(self, request, *args, **kwargs):
        try:
            userlist = request.data
            with transaction.atomic():
                for userid in userlist:
                    user = self.get_object(userid)
                    if request.user == user:
                        canChangeField = perimissionfields.userpermfield['changeself']
                    else:
                        if request.user.has_perm('usersys.admin_changeuser'):
                            canChangeField = perimissionfields.userpermfield['usersys.admin_changeuser']
                        elif request.user.has_perm('usersys.user_changeuser',user):
                            canChangeField = perimissionfields.userpermfield['usersys.trader_changeuser']
                        else:
                            raise InvestError(code=2009)
                    data = request.data
                    data['lastmodifyuser'] = request.user.id
                    data['lastmodifytime'] = datetime.datetime.now()
                    keylist = data.keys()
                    cannoteditlist = [key for key in keylist if key not in canChangeField]
                    if cannoteditlist:
                        raise InvestError(code=2009,msg='没有权限修改_%s' % cannoteditlist)
                    tags = data.pop('tags', None)
                    userserializer = CreatUserSerializer(user, data=data)
                    if userserializer.is_valid():
                        user = userserializer.save()
                        if tags:
                            taglist = Tag.objects.in_bulk(tags)
                            addlist = [item for item in taglist if item not in user.tags.all()]
                            removelist = [item for item in user.tags.all() if item not in taglist]
                            user.user_tags.filter(tag__in=removelist,is_deleted=False).update(is_deleted=True,deletedtime=datetime.datetime.now(),deleteduser=request.user)
                            usertaglist = []
                            for tag in addlist:
                                usertaglist.append(userTags(user=user, tag=tag, createuser=request.user))
                            user.user_tags.bulk_create(usertaglist)
                    else:
                        raise InvestError(code=20071,msg='userdata有误_%s\n%s' % (userserializer.error_messages, userserializer.errors))
                return JSONResponse({'success': True, 'result': userlist, 'errorcode':1000,'errormsg':None})
        except InvestError as err:
            return JSONResponse({'success': False, 'result': None, 'errorcode': err.code, 'errormsg': err.msg})
        except Exception:
            catchexcption(request)
            return JSONResponse({'success': False, 'result': None, 'errorcode': 9999,
                                 'errormsg': traceback.format_exc().split('\n')[-2]})

    #delete
    @loginTokenIsAvailable()
    def destroy(self, request, *args, **kwargs):
        try:
            userlist = request.data
            with transaction.atomic():
                for userid in userlist:
                    instance = self.get_object(userid)
                    if request.user.has_perm('usersys.admin_deleteuser') or request.user.has_perm('usersys.user_deleteuser',instance):
                        pass
                    else:
                        raise InvestError(code=2009)
                    rel_fileds = [f for f in instance._meta.get_fields() if isinstance(f, ForeignObjectRel)]
                    links = [f.get_accessor_name() for f in rel_fileds]
                    for link in links:
                        manager = getattr(instance, link, None)
                        if not manager:
                            continue
                        # one to one
                        if isinstance(manager, models.Model):
                            if hasattr(manager, 'is_deleted') and manager.is_active:
                                raise InvestError(code=2010,msg=u'{} 上有关联数据'.format(link))
                        else:
                            try:
                                manager.model._meta.get_field('is_deleted')
                                if manager.filter(is_active=True).count():
                                    raise InvestError(code=2010,msg=u'{} 上有关联数据'.format(link))
                            except FieldDoesNotExist as ex:
                                if manager.count():
                                    raise InvestError(code=2010,msg=u'{} 上有关联数据'.format(link))
                    instance.is_deleted = True
                    instance.deleteduser = request.user
                    instance.deletedtime = datetime.datetime.utcnow()
                    instance.save()
                    response = {'success': True, 'result': UserSerializer(instance).data, 'errorcode':1000,'errormsg':None}
                    return JSONResponse(response)
        except InvestError as err:
            return JSONResponse({'success': False, 'result': None, 'errorcode': err.code, 'errormsg': err.msg})
        except Exception:
            catchexcption(request)
            return JSONResponse({'success': False, 'result': None, 'errorcode': 9999,
                                 'errormsg': traceback.format_exc().split('\n')[-2]})

    @list_route(methods=['post'])
    def findpassword(self, request, *args, **kwargs):
        try:
            data = request.data
            mobilecode = data.pop('mobilecode', None)
            mobilecodetoken = data.pop('mobilecodetoken', None)
            mobile = data.get('mobile')
            password = data.get('password')
            try:
                mobileauthcode = MobileAuthCode.objects.get(mobile=mobile, code=mobilecode, token=mobilecodetoken)
            except MobileAuthCode.DoesNotExist:
                raise InvestError(code=2005,msg='手机验证码不匹配')
            else:
                if mobileauthcode.isexpired():
                    raise InvestError(code=20051,msg='验证码已过期')
            with transaction.atomic():
                user = self.queryset.get(mobile=mobile)
                user.set_password(password)
                user.save(update_fields=['password'])
                return JSONResponse({'success': True, 'result': password, 'errorcode':1000,'errormsg':None})
        except InvestError as err:
            return JSONResponse({'success': False, 'result': None, 'errorcode': err.code, 'errormsg': err.msg})
        except Exception:
            catchexcption(request)
            return JSONResponse({'success': False, 'result': None, 'errorcode': 9999,
                                 'errormsg': traceback.format_exc().split('\n')[-2]})

    @detail_route(methods=['put'])
    @loginTokenIsAvailable()
    def changepassword(self, request, *args, **kwargs):
        try:
            data = request.data
            oldpassword = data.get('oldpassword')
            password = data.get('password')
            passwordagain = data.get('passwordagain')
            user = self.get_object()
            if user == request.user:
                if user.check_password(oldpassword):
                    raise InvestError(code=2001,msg='密码错误')
                if not password or password != passwordagain:
                    raise InvestError(code=2001,msg='新密码输入有误')
            else:
                raise InvestError(code=2009)
            with transaction.atomic():
                user.set_password(password)
                user.save(update_fields=['password'])
                return JSONResponse({'success': True, 'result': password, 'errorcode':1000,'errormsg':None})
        except InvestError as err:
            return JSONResponse({'success': False, 'result': None, 'errorcode': err.code, 'errormsg': err.msg})
        except Exception:
            catchexcption(request)
            return JSONResponse({'success': False, 'result': None, 'errorcode': 9999,
                                 'errormsg': traceback.format_exc().split('\n')[-2]})

    @detail_route(methods=['get'])
    @loginTokenIsAvailable(['usersys.admin_changeuser'])
    def resetpassword(self,request, *args, **kwargs):
        try:
            user = self.get_object()
            with transaction.atomic():
                user.set_password('Aa123456')
                user.save(update_fields=['password'])
                return JSONResponse({'success': True, 'result': 'Aa123456','errorcode':1000,'errormsg':None})
        except InvestError as err:
            return JSONResponse({'success': False, 'result': None, 'errorcode': err.code, 'errormsg': err.msg})
        except Exception:
            catchexcption(request)
            return JSONResponse({'success': False, 'result': None, 'errorcode': 9999,
                                 'errormsg': traceback.format_exc().split('\n')[-2]})


class UserRelationView(viewsets.ModelViewSet):
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','investoruser', 'traderuser', 'relationtype')
    queryset = UserRelation.objects.filter(is_deleted=False)
    serializer_class = UserRelationSerializer

    @loginTokenIsAvailable(['usersys.admin_getuserrelation','usersys.user_getuserrelation'])
    def list(self, request, *args, **kwargs):
        page_size = request.GET.get('page_size')
        page_index = request.GET.get('page_index')  #从第一页开始
        if not page_size:
            page_size = 10
        if not page_index:
            page_index = 1
        queryset = self.filter_queryset(self.get_queryset())
        if request.user.has_perm('usersys.as_adminuser'):
            queryset = queryset
        elif request.user.has_perm('usersys.as_traderuser'):
            queryset = queryset.filter(traderuser=request.user)
        elif request.user.has_perm('usersys.as_investoruser'):
            queryset = queryset.filter(investoruser=request.user)
        else:
            return JSONResponse({'success':False,'result':None,'errorcode':2009,'errormsg':None})
        try:
            queryset = Paginator(queryset, page_size)
        except EmptyPage:
            return JSONResponse({'success':True,'result':[],'errorcode':1000,'errormsg':None})
        queryset = queryset.page(page_index)
        serializer = self.get_serializer(queryset, many=True)
        return JSONResponse({'success':True,'result':serializer.data,'errorcode':1000,'errormsg':None})


    # @loginTokenIsAvailable()
    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            data['createduser'] = request.user.id
            data['createdtime'] = datetime.datetime.now()
            if request.user.has_perm('usersys.admin_adduserrelation'):
                pass
            elif request.user.has_perm('usersys.user_adduserrelation'):
                data['traderuser'] = request.user.id
            else:
                raise InvestError(code=2009)
            data['createuser'] = request.user.id
            with transaction.atomic():
                newrelation = UserRelationSerializer(data=data)
                if newrelation.is_valid():
                    newrelation.save()
                    response = {'success': True, 'result':newrelation.data,'errorcode':1000,'errormsg':None}
                else:
                    raise InvestError(code=20071,msg='%s'%newrelation.errors)
                return JSONResponse(response)
        except InvestError as err:
            return JSONResponse({'success': False, 'result': None, 'errorcode': err.code, 'errormsg': err.msg})
        except Exception:
            catchexcption(request)
            return JSONResponse({'success': False, 'result': None, 'errorcode': 9999,
                                 'errormsg': traceback.format_exc().split('\n')[-2]})

    def get_object(self,pk=None):
        if pk:
            lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
            assert lookup_url_kwarg in self.kwargs, (
                'Expected view %s to be called with a URL keyword argument '
                'named "%s". Fix your URL conf, or set the `.lookup_field` '
                'attribute on the view correctly.' %
                (self.__class__.__name__, lookup_url_kwarg)
            )
            try:
                obj = UserRelation.objects.get(id=self.kwargs[lookup_url_kwarg], is_deleted=False)
            except UserRelation.DoesNotExist:
                raise InvestError(code=2011, msg='relation with pk = "%s" is not exist' % self.kwargs[lookup_url_kwarg])
        else:
            lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
            assert lookup_url_kwarg in self.kwargs, (
                'Expected view %s to be called with a URL keyword argument '
                'named "%s". Fix your URL conf, or set the `.lookup_field` '
                'attribute on the view correctly.' %
                (self.__class__.__name__, lookup_url_kwarg)
            )
            try:
                obj = UserRelation.objects.get(id=self.kwargs[lookup_url_kwarg],is_deleted=False)
            except UserRelation.DoesNotExist:
                    raise InvestError(code=2011,msg='relation with pk = "%s" is not exist'%self.kwargs[lookup_url_kwarg])
        return obj

    @loginTokenIsAvailable()
    def retrieve(self, request, *args, **kwargs):
        try:
            userrelation = self.get_object()
            if request.user.has_perm('usersys.admin_getuserrelation'):
                pass
            elif request.user.has_perm('usersys.user_getuserrelation'):
                pass
            elif request.user.has_perm('usersys.user_getuserrelation',userrelation):
                pass
            else:
                raise InvestError(code=2009)
            serializer = UserRelationSerializer(userrelation)
            response = {'success':True,'result': serializer.data,'errorcode':1000,'errormsg':None}
            return JSONResponse(response)
        except InvestError as err:
            return JSONResponse({'success': False, 'result': None, 'errorcode': err.code, 'errormsg': err.msg})
        except Exception:
            catchexcption(request)
            return JSONResponse({'success': False, 'result': None, 'errorcode': 9999,'errormsg': traceback.format_exc().split('\n')[-2]})

    @loginTokenIsAvailable()
    def update(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                parmdict = request.data
                relationidlist = parmdict['relationlist']
                relationlist = UserRelation.objects.in_bulk(relationidlist)
                for relation in relationlist:
                    data = parmdict['newdata']
                    if request.user.has_perm('usersys.admin_changeuserrelation'):
                        pass
                    elif request.user.has_perm('usersys.user_changeuserrelation', relation):
                        data['traderuser'] = request.user.id
                        data.pop('relationtype', None)
                    else:
                        raise InvestError(code=2009,msg='没有权限')
                    data['lastmodifyuser'] = request.user.id
                    data['lastmodifytime'] = datetime.datetime.now()

                    newrelation = UserRelationSerializer(relation,data=data)
                    if newrelation.is_valid():
                        newrelation.save()
                    else:
                        raise InvestError(code=20071,msg=newrelation.errors)
                return JSONResponse({'success': True, 'result':UserRelationSerializer(relationlist,many=True).data, 'errorcode':1000,'errormsg':None})
        except InvestError as err:
            return JSONResponse({'success': False, 'result': None, 'errorcode': err.code, 'errormsg': err.msg})
        except Exception:
            catchexcption(request)
            return JSONResponse({'success': False, 'result': None, 'errorcode': 9999,
                                 'errormsg': traceback.format_exc().split('\n')[-2]})

    @loginTokenIsAvailable()
    def destroy(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                relationidlist = request.data
                relationlist = self.queryset.in_bulk(relationidlist)
                for userrelation in relationlist:
                    if request.user.has_perm('usersys.user_deleteuserrelation',userrelation):
                        pass
                    elif request.user.has_perm('usersys.admin_deleteuserrelation'):
                        pass
                    else:
                        raise InvestError(code=2009,msg='没有权限')
                    userrelation.is_deleted = True
                    userrelation.deleteduser = request.user
                    userrelation.deletedtime = datetime.datetime.now()
                    userrelation.save()
                response = {'success': True, 'result': UserRelationSerializer(relationlist,many=True).data,'errorcode':1000,'errormsg':None}
                return JSONResponse(response)
        except InvestError as err:
            return JSONResponse({'success': False, 'result': None, 'errorcode': err.code, 'errormsg': err.msg})
        except Exception:
            catchexcption(request)
            return JSONResponse({'success': False, 'result': None, 'errorcode': 9999,
                                 'errormsg': traceback.format_exc().split('\n')[-2]})


@api_view(['POST'])
def login(request):
    try:
        receive = request.data
        username = receive['account']
        password = receive['password']
        if not username or not password:
            raise InvestError(code=20071,msg='参数不全')
        clienttype = request.META.get('HTTP_CLIENTTYPE')
        user = auth.authenticate(username=username, password=password)
        if not user or not clienttype:
            if not clienttype:
                raise InvestError(code=2003,msg='登录类型不可用')
            else:
                raise InvestError(code=2001,msg='密码错误')
        user.last_login = datetime.datetime.now()
        if user.is_active:
            user.is_active = True
        user.save()
        response = maketoken(user, clienttype)
        return JSONResponse({"result": response, "success": True, 'errorcode':1000,'errormsg':None})
    except InvestError as err:
            return JSONResponse({'success': False, 'result': None, 'errorcode':err.code,'errormsg':err.msg})
    except Exception:
            catchexcption(request)
            return JSONResponse({'success': False, 'result': None,'errorcode':9999, 'errormsg': traceback.format_exc().split('\n')[-2]})



