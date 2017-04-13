#coding=utf-8
import traceback

import datetime
from django.contrib import auth
from django.contrib.auth.models import Group
from django.core.exceptions import FieldDoesNotExist
from django.core.paginator import Paginator, EmptyPage
from django.db import transaction,models

# Create your views here.
from django.db.models import Q
from django.db.models.fields.reverse_related import ForeignObjectRel
from rest_framework import filters
from rest_framework import viewsets

from rest_framework.decorators import api_view, detail_route, list_route
from usersys.models import MyUser, MyToken, UserRelation, userTags, MobileAuthCode
from usersys.serializer import UserSerializer, UserListSerializer, UserRelationSerializer,\
    CreatUserSerializer , UserCommenSerializer
from sourcetype.models import ClientType, Tag
from utils import perimissionfields
from utils.util import read_from_cache, write_to_cache, loginTokenIsAvailable, JSONResponse,\
    permissiondeniedresponse, catchexcption, cache_delete_key


class UserView(viewsets.ModelViewSet):
    filter_backends = (filters.DjangoFilterBackend,)
    queryset = MyUser.objects.filter(is_deleted=False)
    filter_fields = ('mobile','email','name','id','groups')
    serializer_class = UserSerializer
    redis_key = 'users'
    Model = MyUser

    def get_object(self):
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
                raise ValueError('obj with this "%s" is not exist'%self.kwargs[lookup_url_kwarg])
            else:
                write_to_cache(self.redis_key+'_%s'%self.kwargs[lookup_url_kwarg],obj)
        return obj

    @loginTokenIsAvailable(['usersys.as_adminuser'])
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
            return JSONResponse({'success':True,'result':[],'error':None})
        queryset = queryset.page(page_index)
        serializer = UserListSerializer(queryset, many=True)
        return JSONResponse({'success':True,'result': serializer.data,'error': None,})

    #注册用户(新注册用户没有交易师)
    @transaction.atomic
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
                        raise ValueError('手机验证码不匹配')
                    else:
                        if mobileauthcode.isexpired():
                            raise ValueError('验证码已过期')
                    if email:
                        filterQ = Q(mobile=mobile) | Q(email=email)
                    else:
                        filterQ = Q(mobile=mobile)
                elif email:
                    filterQ = Q(email=email)
                else:
                    raise KeyError('mobile、email至少有一项不能为空')
                try:
                    self.queryset.get(filterQ)
                except MyUser.DoesNotExist:
                    pass
                else:
                    raise ValueError('user has been already exist')
                user = MyUser(email=email, mobile=mobile)
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
                    raise ValueError('userdata有误_%s\n%s' % (userserializer.error_messages, userserializer.errors))
                return JSONResponse({'success': True, 'result': UserSerializer(user).data, 'error': None, })
        except Exception:
            catchexcption(request)
            return JSONResponse({'success': False, 'result': None, 'error': traceback.format_exc().split('\n')[-2]})

    # 新增用户
    @loginTokenIsAvailable()
    def adduser(self, request, *args, **kwargs):
        data = request.data
        if request.user.has_perm('usersys.admin_adduser'):
            canCreateField = perimissionfields.userpermfield['usersys.admin_adduser']
        elif request.user.has_perm('usersys.trader_adduser'):
            canCreateField = perimissionfields.userpermfield['usersys.trader_adduser']
        else:
            return JSONResponse(permissiondeniedresponse)
        try:
            with transaction.atomic():
                password = data.get('password')
                email = data.get('email')
                mobile = data.get('mobile')
                try:
                    user = self.get_queryset().get(Q(mobile=mobile) | Q(email=email))
                except MyUser.DoesNotExist:
                    pass
                else:
                    raise ValueError('user with this mobile or email has already been exist')
                user = MyUser()
                user.set_password(password)
                user.save()
                keylist = data.keys()
                cannoteditlist = [key for key in keylist if key not in canCreateField]
                if cannoteditlist:
                    raise KeyError('没有权限修改%s' % cannoteditlist)
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
                    raise ValueError('userdata有误_%s\n%s' % (userserializer.error_messages, userserializer.errors))
                return JSONResponse({'success': True, 'result': UserSerializer(user).data, 'error': None, })
        except Exception:
            catchexcption(request)
            return JSONResponse({'success': False, 'result': None, 'error': traceback.format_exc().split('\n')[-2], })


    #get
    @loginTokenIsAvailable()
    def retrieve(self, request, *args, **kwargs):
        try:
            user = self.get_object()
            if request.user == user:
                userserializer = UserListSerializer
            else:
                if request.user.has_perm('usersys.as_adminuser'):
                    userserializer = UserListSerializer
                elif request.user.has_perm('usersys.trader_changeuser',self.get_object()):
                    userserializer = UserListSerializer
                else:
                    return JSONResponse(permissiondeniedresponse)
            serializer = userserializer(user)
            return JSONResponse({'success':True,'result': serializer.data,'error': None})

        except Exception:
            catchexcption(request)
            return JSONResponse({'success':False,'result': None,'error': traceback.format_exc().split('\n')[-2],})

    @detail_route(methods=['get'])
    @loginTokenIsAvailable()
    def getdetailinfo(self, request, *args, **kwargs):
        try:
            user = self.get_object()
            if request.user == user:
                userserializer = UserSerializer
            else:
                if request.user.has_perm('usersys.as_adminuser'):
                    userserializer = UserSerializer
                elif request.user.has_perm('usersys.trader_changeuser', self.get_object()):
                    userserializer = UserSerializer
                else:
                    return JSONResponse(permissiondeniedresponse)
            serializer = userserializer(user)
            response = {'success': True, 'result': serializer.data, 'error': None, }
            return JSONResponse(response)
        except Exception:
            catchexcption(request)
            response = {'success': False, 'result': None, 'error': traceback.format_exc().split('\n')[-2], }
            return JSONResponse(response)

    #patch
    @loginTokenIsAvailable()
    def partial_update(self, request, *args, **kwargs):
        try:
            user = self.get_object()
            if request.user == user:
                canChangeField = perimissionfields.userpermfield['changeself']
            else:
                if request.user.has_perm('usersys.admin_changeuser'):
                    canChangeField = perimissionfields.userpermfield['usersys.admin_changeuser']
                elif request.user.has_perm('usersys.trader_changeuser',self.get_object()):
                    canChangeField = perimissionfields.userpermfield['usersys.trader_changeuser']
                else:
                    raise ValueError('没有权限')
            data = request.data
            keylist = data.keys()
            cannoteditlist = [key for key in keylist if key not in canChangeField]
            if cannoteditlist:
                raise ValueError('没有权限修改_%s' % cannoteditlist)
            with transaction.atomic():
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
                    raise ValueError('userdata有误_%s\n%s' % (userserializer.error_messages, userserializer.errors))
                return JSONResponse({'success': True, 'result': UserSerializer(user).data, 'error': None, })
        except Exception:
            catchexcption(request)
            return JSONResponse({'success': False, 'result': None, 'error': traceback.format_exc().split('\n')[-2], })

    #delete
    @loginTokenIsAvailable(['usersys.as_adminuser'])
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            rel_fileds = [f for f in instance._meta.get_fields() if isinstance(f, ForeignObjectRel)]
            links = [f.get_accessor_name() for f in rel_fileds]
            for link in links:
                manager = getattr(instance, link, None)
                if not manager:
                    continue
                # one to one
                if isinstance(manager, models.Model):
                    if hasattr(manager, 'is_deleted') and manager.is_active:
                        raise ValueError(u'{} 上有关联数据'.format(link))
                else:
                    try:
                        manager.model._meta.get_field('is_deleted')
                        if manager.filter(is_active=True).count():
                            raise ValueError(u'{} 上有关联数据'.format(link))
                    except FieldDoesNotExist as ex:
                        if manager.count():
                            raise ValueError(u'{} 上有关联数据'.format(link))
            with transaction.atomic():
                instance.is_deleted = True
                instance.deleteduser = request.user
                instance.deletedtime = datetime.datetime.utcnow()
                instance.save()
                response = {'success': True, 'result': UserSerializer(instance).data, 'error': None}
                return JSONResponse(response)
        except:
            catchexcption(request)
            response = {'success': False, 'result': None, 'error': traceback.format_exc().split('\n')[-2], }
            return JSONResponse(response)

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
                raise ValueError('手机验证码不匹配')
            else:
                if mobileauthcode.isexpired():
                    raise ValueError('验证码已过期')
            with transaction.atomic():
                user = self.queryset.get(mobile=mobile)
                user.set_password(password)
                user.save(update_fields=['password'])
                return JSONResponse({'success': True, 'result': password, 'error': None})
        except:
            return JSONResponse({'success': False, 'result': None, 'error': traceback.format_exc().split('\n')[-2],})

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
                    raise ValueError('密码错误')
                if not password or password != passwordagain:
                    raise ValueError('新密码输入有误')
            else:
                raise ValueError('没有权限')
            with transaction.atomic():
                user.set_password(password)
                user.save(update_fields=['password'])
                return JSONResponse({'success': True, 'result': password, 'error': None})
        except:
            return JSONResponse({'success': False, 'result': None, 'error': traceback.format_exc().split('\n')[-2],})

    @detail_route(methods=['get'])
    @loginTokenIsAvailable(['usersys.as_adminuser'])
    def resetpassword(self,request, *args, **kwargs):
        try:
            user = self.get_object()
            with transaction.atomic():
                user.set_password('Aa123456')
                user.save(update_fields=['password'])
                return JSONResponse({'success': True, 'result': 'Aa123456', 'error': None})
        except:
            return JSONResponse({'success': False, 'result': None, 'error': traceback.format_exc().split('\n')[-2], })


class UserRelationView(viewsets.ModelViewSet):
    filter_backends = (filters.DjangoFilterBackend,)
    # permission_classes = (AllowAny,)
    filter_fields = ('id','investoruser', 'traderuser', 'relationtype')
    queryset = UserRelation.objects.filter(is_deleted=False)
    serializer_class = UserRelationSerializer

    @loginTokenIsAvailable(['usersys.as_adminuser','usersys.as_traderuser','usersys.as_investoruser'])
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
            return JSONResponse({'success':False,'result':None,'error':'no permission'})
        try:
            queryset = Paginator(queryset, page_size)
        except EmptyPage:
            return JSONResponse({'success':True,'result':[],'error':None})
        queryset = queryset.page(page_index)
        serializer = self.get_serializer(queryset, many=True)
        return JSONResponse({'success':True,'result':serializer.data,'error':None})


    @loginTokenIsAvailable()
    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            if request.user.has_perm('usersys.admin_adduserrelation'):
                pass
            elif request.user.has_perm('usersys.add_userrelation'):
                data['traderuser'] = request.user.id
            else:
                raise ValueError('没有权限')
            data['createuser'] = request.user.id
            with transaction.atomic():
                newrelation = UserRelationSerializer(data=data)
                if newrelation.is_valid():
                    newrelation.save()
                    response = {'success': True, 'result':newrelation.data, 'error': None}
                else:
                    raise ValueError('%s'%newrelation.errors)
                return JSONResponse(response)
        except:
            catchexcption(request)
            response = {'success': False, 'result': None, 'error': traceback.format_exc().split('\n')[-2], }
            return JSONResponse(response)

    def get_object(self):
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
                raise ValueError('obj with pk = "%s" is not exist'%self.kwargs[lookup_url_kwarg])
        return obj

    @loginTokenIsAvailable()
    def retrieve(self, request, *args, **kwargs):
        try:
            userrelation = self.get_object()
            if request.user.has_perm('usersys.as_adminuser'):
                pass
            elif request.user == userrelation.traderuser or request.user == userrelation.investoruser:
                pass
            else:
                raise ('没有权限')
            serializer = UserRelationSerializer(userrelation)
            response = {'success':True,'result': serializer.data,'error': None,}
            return JSONResponse(response)
        except:
            catchexcption(request)
            response = {'success': False, 'result': None, 'error': traceback.format_exc().split('\n')[-2], }
            return JSONResponse(response)

    @loginTokenIsAvailable()
    def update(self, request, *args, **kwargs):
        try:
            data = request.data
            relation = self.get_object()
            if request.user.has_perm('usersys.admin_changeuserrelation'):
                pass
            elif request.user.has_perm('usersys.change_userrelation', relation):
                data['traderuser'] = request.user.id
                data.pop('relationtype', None)
            else:
                raise ('没有权限')
            data['lastmodifyuser'] = request.user.id
            data['lastmodifytime'] = datetime.datetime.now()
            with transaction.atomic():
                newrelation = UserRelationSerializer(relation,data=data)
                if newrelation.is_valid():
                    newrelation.save()
                    response = {'success': True, 'result':newrelation.data, 'error': None}
                else:
                    raise ValueError('err:%s'%newrelation.errors)
                return JSONResponse(response)
        except:
            catchexcption(request)
            response = {'success': False, 'result': None, 'error': traceback.format_exc().split('\n')[-2], }
            return JSONResponse(response)

    @loginTokenIsAvailable()
    def destroy(self, request, *args, **kwargs):
        try:
            userrelation = self.get_object()
            if request.user.has_perm('usersys.delete_userrelation',userrelation):
                pass
            elif request.user.has_perm('usersys.admin_deleteuserrelation'):
                pass
            else:
                raise ('没有权限')
            with transaction.atomic():
                userrelation.is_deleted = True
                userrelation.deleteduser = request.user
                userrelation.deletedtime = datetime.datetime.now()
                userrelation.save()
                response = {'success': True, 'result': UserRelationSerializer(userrelation).data, 'error': None}
                return JSONResponse(response)
        except:
            catchexcption(request)
            response = {'success': False, 'result': None, 'error': traceback.format_exc().split('\n')[-2], }
            return JSONResponse(response)



@api_view(['POST'])
def login(request):
    try:
        receive = request.data
        username = receive['account']
        password = receive['password']
        clienttype = request.META.get('HTTP_CLIENTTYPE')
        user = auth.authenticate(username=username, password=password)
        if not user or not clienttype:
            if not clienttype:
                raise ValueError(u'登录类型不可用')
            else:
                raise ValueError(u'账号密码有误')
        response = maketoken(user, clienttype)
        return JSONResponse({"result": response, "success": True, 'error': None, })
    except Exception:
        response = {'success': False, 'result': None, 'error': traceback.format_exc().split('\n')[-2], }
        return JSONResponse(response)



def maketoken(user,clienttype):
    try:
        tokens = MyToken.objects.filter(user=user, clienttype__id=clienttype, is_deleted=False)
    except MyToken.DoesNotExist:
        pass
    except Exception as excp:
        raise ValueError(repr(excp))
    else:
        for token in tokens:
            token.is_deleted = True
            token.save(update_fields=['is_deleted'])
    type = ClientType.objects.get(id=clienttype)
    token = MyToken.objects.create(user=user, clienttype=type)
    serializer = UserListSerializer(user)
    response = serializer.data
    return {'token':token.key,
        "user_info": response,
    }
