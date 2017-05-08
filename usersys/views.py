#coding=utf-8
import traceback

import datetime
from django.contrib import auth
from django.core.cache import cache
from django.core.exceptions import FieldDoesNotExist
from django.core.paginator import Paginator, EmptyPage
from django.db import transaction,models

# Create your views here.
from django.db.models import Q
from django.db.models import QuerySet
from django.db.models.fields.reverse_related import ForeignObjectRel
from guardian.shortcuts import assign_perm
from rest_framework import filters
from rest_framework import viewsets

from rest_framework.decorators import api_view, detail_route, list_route

from third.models import MobileAuthCode
from usersys.models import MyUser, MyToken, UserRelation, userTags, MyUserBackend, UserFriendship
from usersys.serializer import UserSerializer, UserListSerializer, UserRelationSerializer,\
    CreatUserSerializer , UserCommenSerializer , UserRelationDetailSerializer, UserFriendshipSerializer, \
    UserFriendshipDetailSerializer, UserFriendshipUpdateSerializer
from sourcetype.models import Tag, DataSource
from utils import perimissionfields
from utils.myClass import JSONResponse, InvestError
from utils.util import read_from_cache, write_to_cache, loginTokenIsAvailable,\
    catchexcption, cache_delete_key, maketoken, returnDictChangeToLanguage, returnListChangeToLanguage, SuccessResponse, \
    InvestErrorResponse, ExceptionResponse, checkIPAddress


class UserView(viewsets.ModelViewSet):
    """
    list:用户列表
    create:注册用户
    adduser:新增用户
    retrieve:查看某一用户基本信息
    getdetailinfo:查看某一用户详细信息
    findpassword:找回密码
    changepassword:修改密码
    resetpassword:重置密码
    update:修改用户信息
    destroy:删除用户

    """
    filter_backends = (filters.DjangoFilterBackend,)
    queryset = MyUser.objects.filter(is_deleted=False)
    filter_fields = ('mobile','email','nameC','nameE','groups','org')
    serializer_class = UserSerializer
    redis_key = 'user'
    Model = MyUser

    def get_queryset(self):
        assert self.queryset is not None, (
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method."
            % self.__class__.__name__
        )
        queryset = self.queryset
        if isinstance(queryset, QuerySet):
            if self.request.user.is_authenticated:
                queryset = queryset.filter(datasource=self.request.user.datasource)
            else:
                queryset = queryset.all()
        else:
            raise InvestError(code=8890)
        return queryset

    def get_object(self,pk=None):
        if pk:
            obj = read_from_cache(self.redis_key + '_%s' % pk)
            if not obj:
                try:
                    obj = self.queryset.get(id=pk)
                except self.Model.DoesNotExist:
                    raise InvestError(code=2002)
                else:
                    write_to_cache(self.redis_key + '_%s' % pk, obj)
        else:
            lookup_url_kwarg = 'pk'
            obj = read_from_cache(self.redis_key+'_%s'%self.kwargs[lookup_url_kwarg])
            if not obj:
                try:
                    obj = self.queryset.get(id=self.kwargs[lookup_url_kwarg])
                except self.Model.DoesNotExist:
                    raise InvestError(code=2002)
                else:
                    write_to_cache(self.redis_key+'_%s'%self.kwargs[lookup_url_kwarg],obj)
        if obj.datasource != self.request.user.datasource:
            raise InvestError(code=8888,msg='资源非同源')
        return obj

    @loginTokenIsAvailable()
    def list(self, request, *args, **kwargs):
        try:
            page_size = request.GET.get('page_size')
            page_index = request.GET.get('page_index') #从第一页开始
            lang = request.GET.get('lang')
            if not page_size:
                page_size = 10
            if not page_index:
                page_index = 1
            queryset = self.filter_queryset(self.get_queryset())
            if request.user.has_perm('usersys.admin_getuser'):
                serializer_class = UserListSerializer
            else:
                serializer_class = UserCommenSerializer
            try:
                queryset = Paginator(queryset, page_size)
            except EmptyPage:
                raise InvestError(code=1001)
            queryset = queryset.page(page_index)
            serializer = serializer_class(queryset, many=True)
            return JSONResponse(SuccessResponse(returnListChangeToLanguage(serializer.data,lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    #注册用户(新注册用户没有交易师)
    def create(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                data = request.data
                lang = request.GET.get('lang')
                mobilecode = data.pop('mobilecode', None)
                mobilecodetoken = data.pop('mobilecodetoken', None)
                mobile = data.get('mobile')
                email = data.get('email')
                source = data.pop('datasource',None)
                if source:
                    datasource = DataSource.objects.filter(id=source,is_deleted=False)
                    if datasource.exists():
                        userdatasource = datasource.first()
                    else:
                        raise  InvestError(code=8888)
                else:
                    raise InvestError(code=8888,msg='source field is required')
                if mobile:
                    if not mobilecodetoken or not mobilecode:
                        raise InvestError(code=20072,msg='验证码缺失')
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
                    raise InvestError(code=2007,msg='mobile、email cannot all be null')
                if self.queryset.filter(filterQ,datasource=userdatasource).exists():
                    raise InvestError(code=2004)
                user = MyUser(email=email,mobile=mobile,datasource=userdatasource)
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
                            usertaglist.append(userTags(user=user, tag_id=tag, createdtime=datetime.datetime.now()))
                        user.user_usertags.bulk_create(usertaglist)
                else:
                    raise InvestError(code=20071,msg='%s\n%s' % (userserializer.error_messages, userserializer.errors))
                returndic = UserSerializer(user).data
                return JSONResponse(SuccessResponse(returnDictChangeToLanguage(returndic,lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    # 新增用户
    @loginTokenIsAvailable()
    def adduser(self, request, *args, **kwargs):
        data = request.data
        data['createduser'] = request.user.id
        data['createdtime'] = datetime.datetime.now()
        data['datasource'] = request.user.datasource.id
        if request.user.has_perm('usersys.admin_adduser'):
            canCreateField = perimissionfields.userpermfield['usersys.admin_adduser']
        elif request.user.has_perm('usersys.user_adduser'):
            canCreateField = perimissionfields.userpermfield['usersys.trader_adduser']
        else:
            return JSONResponse({'result': None, 'success': False, 'errorcode':2009,'errormsg':'没有新增权限'})
        try:
            with transaction.atomic():
                password = data.pop('password','Aa123456')
                email = data.get('email')
                mobile = data.get('mobile')
                if not email and not mobile:
                    raise InvestError(code=2007)
                if self.get_queryset().filter(Q(mobile=mobile) | Q(email=email)).exists():
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
                        user.user_usertags.bulk_create(usertaglist)
                else:
                    raise InvestError(code=20071,msg='userdata有误_%s\n%s' % (userserializer.error_messages, userserializer.errors))
                if user.createuser:
                    assign_perm('usersys.user_getuser', user.createuser, user)
                    assign_perm('usersys.user_changeuser', user.createuser, user)
                    assign_perm('usersys.user_deleteuser', user.createuser, user)
                return JSONResponse(SuccessResponse(returnDictChangeToLanguage(UserSerializer(user).data)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    #get
    @loginTokenIsAvailable()
    def retrieve(self, request, *args, **kwargs):
        try:
            lang = request.GET.get('lang')
            user = self.get_object()
            serializer = UserCommenSerializer(user)
            return JSONResponse(SuccessResponse(returnDictChangeToLanguage(serializer.data,lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @detail_route(methods=['get'])
    @loginTokenIsAvailable()
    def getdetailinfo(self, request, *args, **kwargs):
        try:
            lang = request.GET.get('lang')
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
            return JSONResponse(SuccessResponse(returnDictChangeToLanguage(serializer.data,lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    #put
    @loginTokenIsAvailable()
    def update(self, request, *args, **kwargs):
        try:
            lang = request.GET.get('lang')
            useridlist = request.data
            userlist = []
            with transaction.atomic():
                for userid in useridlist:
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
                        cache_delete_key(self.redis_key + '_%s' % user.id)
                        if tags:
                            taglist = Tag.objects.in_bulk(tags)
                            addlist = [item for item in taglist if item not in user.tags.all()]
                            removelist = [item for item in user.tags.all() if item not in taglist]
                            user.user_usertags.filter(tag__in=removelist,is_deleted=False).update(is_deleted=True,deletedtime=datetime.datetime.now(),deleteduser=request.user)
                            usertaglist = []
                            for tag in addlist:
                                usertaglist.append(userTags(user=user, tag=tag, createuser=request.user))
                            user.user_usertags.bulk_create(usertaglist)
                    else:
                        raise InvestError(code=20071,msg='userdata有误_%s\n%s' % (userserializer.error_messages, userserializer.errors))
                    userlist.append(userserializer.data)
                return JSONResponse(SuccessResponse(returnListChangeToLanguage(userlist,lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    #delete
    @loginTokenIsAvailable()
    def destroy(self, request, *args, **kwargs):
        try:
            useridlist = request.data
            userlist = []
            lang = request.GET.get('lang')
            if not useridlist:
                raise InvestError(code=20071,msg='except a not null list')
            with transaction.atomic():
                rel_fileds = [f for f in MyUser._meta.get_fields() if isinstance(f, ForeignObjectRel)]
                links = [f.get_accessor_name() for f in rel_fileds]
                for userid in useridlist:
                    instance = self.get_object(userid)
                    if request.user.has_perm('usersys.admin_deleteuser') or request.user.has_perm('usersys.user_deleteuser',instance):
                        pass
                    else:
                        raise InvestError(code=2009)
                    for link in links:
                        if link in ['investor_relations','trader_relations','investor_timelines','supporter_timelines','trader_timelines']:
                            manager = getattr(instance, link, None)
                            if not manager:
                                continue
                            # one to one
                            if isinstance(manager, models.Model):
                                if hasattr(manager, 'is_deleted') and not manager.is_deleted:
                                    raise InvestError(code=2010,msg=u'{} 上有关联数据'.format(link))
                            else:
                                try:
                                    manager.model._meta.get_field('is_deleted')
                                    if manager.all().filter(is_deleted=False).count():
                                        raise InvestError(code=2010,msg=u'{} 上有关联数据'.format(link))
                                except FieldDoesNotExist:
                                    if manager.all().count():
                                        raise InvestError(code=2010,msg=u'{} 上有关联数据'.format(link))
                        # else:
                        #     manager = getattr(instance, link, None)
                        #     if not manager:
                        #         continue
                        #     # one to one
                        #     if isinstance(manager, models.Model):
                        #         if hasattr(manager, 'is_deleted') and not manager.is_deleted:
                        #             manager.is_deleted = True
                        #             manager.save()
                        #     else:
                        #         try:
                        #             manager.model._meta.get_field('is_deleted')
                        #             if manager.all().filter(is_deleted=False).count():
                        #                 manager.all().update(is_deleted=True)
                        #         except FieldDoesNotExist:
                        #             if manager.all().count():
                        #                 raise InvestError(code=2010, msg=u'{} 上有关联数据，且没有is_deleted字段'.format(link))
                    instance.is_deleted = True
                    instance.deleteduser = request.user
                    instance.deletedtime = datetime.datetime.now()
                    instance.save()
                    instance.user_usertags.all().update(is_deleted=True)
                    cache_delete_key(self.redis_key + '_%s' % instance.id)
                    userlist.append(UserSerializer(instance).data)
                return JSONResponse(SuccessResponse(returnListChangeToLanguage(userlist,lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @list_route(methods=['post'])
    def findpassword(self, request, *args, **kwargs):
        try:
            data = request.data
            mobilecode = data.pop('mobilecode', None)
            mobilecodetoken = data.pop('mobilecodetoken', None)
            mobile = data.get('mobile')
            password = data.get('password')
            source = data.pop('datasource', None)
            if source:
                datasource = DataSource.objects.filter(id=source, is_deleted=False)
                if datasource.exists():
                    userdatasource = datasource.first()
                else:
                    raise InvestError(code=8888)
            else:
                raise InvestError(code=8888, msg='source field is required')
            try:
                user = self.get_queryset().get(mobile=mobile, datasource=userdatasource)
            except MyUser.DoesNotExist:
                raise InvestError(code=2002,msg='用户不存在——%s'%source)
            try:
                mobileauthcode = MobileAuthCode.objects.get(mobile=mobile, code=mobilecode, token=mobilecodetoken)
            except MobileAuthCode.DoesNotExist:
                raise InvestError(code=2005,msg='手机验证码不匹配')
            else:
                if mobileauthcode.isexpired():
                    raise InvestError(code=20051,msg='验证码已过期')
            with transaction.atomic():
                user.set_password(password)
                user.save(update_fields=['password'])
                cache_delete_key(self.redis_key + '_%s' % user.id)
                return JSONResponse(SuccessResponse(password))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

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
                cache_delete_key(self.redis_key + '_%s' % user.id)
                return JSONResponse(SuccessResponse(password))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @detail_route(methods=['get'])
    @loginTokenIsAvailable(['usersys.admin_changeuser'])
    def resetpassword(self,request, *args, **kwargs):
        try:
            user = self.get_object()
            with transaction.atomic():
                user.set_password('Aa123456')
                user.save(update_fields=['password'])
                cache_delete_key(self.redis_key + '_%s' % user.id)
                return JSONResponse(SuccessResponse('Aa123456'))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))


class UserRelationView(viewsets.ModelViewSet):
    """
    list:获取用户业务关系联系人
    create:添加业务关系联系人
    retrieve:查看业务关系联系人详情
    update:修改业务关系联系人(批量)
    destroy:删除业务关系联系人(批量)
    """
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','investoruser', 'traderuser', 'relationtype')
    queryset = UserRelation.objects.filter(is_deleted=False)
    serializer_class = UserRelationSerializer

    def get_queryset(self):
        assert self.queryset is not None, (
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method."
            % self.__class__.__name__
        )
        queryset = self.queryset
        if isinstance(queryset, QuerySet):
            if self.request.user.is_authenticated:
                queryset = queryset.filter(datasource=self.request.user.datasource)
            else:
                queryset = queryset.all()
        else:
            raise InvestError(code=8890)
        return queryset

    @loginTokenIsAvailable(['usersys.admin_getuserrelation','usersys.user_getuserrelation'])
    def list(self, request, *args, **kwargs):
        try:
            page_size = request.GET.get('page_size')
            page_index = request.GET.get('page_index')  #从第一页开始
            lang = request.GET.get('lang')
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
                raise InvestError(code=2009)
            try:
                queryset = Paginator(queryset, page_size)
            except EmptyPage:
                raise InvestError(code=1001)
            queryset = queryset.page(page_index)
            serializer = self.get_serializer(queryset, many=True)
            return JSONResponse(SuccessResponse(returnListChangeToLanguage(serializer.data,lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))


    @loginTokenIsAvailable()
    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            data['createduser'] = request.user.id
            data['datasource'] = request.user.datasource.id
            lang = request.GET.get('lang')
            if request.user.has_perm('usersys.admin_adduserrelation'):
                pass
            elif request.user.has_perm('usersys.user_adduserrelation'):
                data['traderuser'] = request.user.id
            else:
                raise InvestError(code=2009)
            with transaction.atomic():
                newrelation = UserRelationDetailSerializer(data=data)
                if newrelation.is_valid():
                    relation = newrelation.save()
                    assign_perm('usersys.user_getuserrelation', relation.traderuser, relation)
                    assign_perm('usersys.user_changeuserrelation', relation.traderuser, relation)
                    assign_perm('usersys.user_deleteuserrelation', relation.traderuser, relation)
                else:
                    raise InvestError(code=20071,msg='%s'%newrelation.errors)
                return JSONResponse(SuccessResponse(returnDictChangeToLanguage(newrelation.data,lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

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
        if obj.datasource != self.request.user.datasource:
            raise InvestError(code=8888,msg='资源非同源')
        return obj

    @loginTokenIsAvailable()
    def retrieve(self, request, *args, **kwargs):
        try:
            userrelation = self.get_object()
            lang = request.GET.get('lang')
            if request.user.has_perm('usersys.admin_getuserrelation'):
                pass
            elif request.user.has_perm('usersys.user_getuserrelation',userrelation):
                pass
            else:
                raise InvestError(code=2009)
            serializer = UserRelationSerializer(userrelation)
            return JSONResponse(SuccessResponse(returnDictChangeToLanguage(serializer.data,lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable()
    def update(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                parmdict = request.data
                lang = request.GET.get('lang')
                relationidlist = parmdict['relationlist']
                relationlist = self.get_queryset().in_bulk(relationidlist)
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
                return JSONResponse(SuccessResponse(returnListChangeToLanguage(UserRelationSerializer(relationlist,many=True).data,lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable()
    def destroy(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                relationidlist = request.data
                lang = request.GET.get('lang')
                relationlist = self.get_queryset().in_bulk(relationidlist)
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
                return JSONResponse(SuccessResponse(returnListChangeToLanguage(UserRelationSerializer(relationlist,many=True),lang).data))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))


class UserFriendshipView(viewsets.ModelViewSet):
    """
    list:获取用户好友列表
    create:添加好友 (管理员权限可以直接确认关系，非管理员权限需对方确认)
    update:同意添加好友、修改查看项目收藏权限
    destroy:删除好友关系
    """
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('user', 'friend', 'isaccept')
    queryset = UserFriendship.objects.filter(is_deleted=False)
    serializer_class = UserFriendshipSerializer

    def get_queryset(self):
        assert self.queryset is not None, (
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method."
            % self.__class__.__name__
        )
        queryset = self.queryset
        if isinstance(queryset, QuerySet):
            if self.request.user.is_authenticated:
                queryset = queryset.filter(datasource=self.request.user.datasource)
            else:
                queryset = queryset.all()
        else:
            raise InvestError(code=8890)
        return queryset

    def get_object(self,pk=None):
        if pk:
            try:
                obj = self.queryset.get(id=pk)
            except UserFriendship.DoesNotExist:
                raise InvestError(code=2002)
        else:
            try:
                obj = self.queryset.get(id=self.kwargs['pk'])
            except UserFriendship.DoesNotExist:
                raise InvestError(code=2002)
        if obj.datasource != self.request.user.datasource:
            raise InvestError(code=8888,msg='资源非同源')
        return obj

    @loginTokenIsAvailable()
    def list(self, request, *args, **kwargs):
        try:
            page_size = request.GET.get('page_size')
            page_index = request.GET.get('page_index')
            lang = request.GET.get('lang')
            if not page_size:
                page_size = 10
            if not page_index:
                page_index = 1
            queryset = self.filter_queryset(self.get_queryset())
            if request.user.has_perm('usersys.admin_getfriend'):
                queryset = queryset
            else:
                queryset = queryset.filter(Q(user=request.user) | Q(friend=request.user))
            try:
                queryset = Paginator(queryset, page_size)
            except EmptyPage:
                raise InvestError(code=1001)
            queryset = queryset.page(page_index)
            serializer = UserFriendshipSerializer(queryset, many=True)
            return JSONResponse(SuccessResponse(returnListChangeToLanguage(serializer.data,lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            data['createduser'] = request.user.id
            data['datasource'] = 1
            lang = request.GET.get('lang')
            if request.user.has_perm('usersys.admin_addfriend'):
                pass
            else:
                data['user'] = request.user.id
                data['isaccept'] = False
                data['accepttime'] = None
            with transaction.atomic():
                newfriendship = UserFriendshipDetailSerializer(data=data)
                if newfriendship.is_valid():
                    newfriendship.save()
                else:
                    raise InvestError(code=20071,msg='%s'%newfriendship.errors)
                return JSONResponse(SuccessResponse(returnDictChangeToLanguage(newfriendship.data,lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable()
    def update(self, request, *args, **kwargs):
        try:
            data = request.data
            lang = request.GET.get('lang')
            instance = self.get_object()
            if request.user.has_perm('usersys.admin_changefriend'):
                pass
            elif request.user == instance.user or request.user == instance.friend:
                pass
            else:
                raise InvestError(code=2009)
            with transaction.atomic():
                newfriendship = UserFriendshipUpdateSerializer(instance,data=data)
                if newfriendship.is_valid():
                    newfriendship.save()
                else:
                    raise InvestError(code=20071, msg='%s' % newfriendship.errors)
                return JSONResponse(SuccessResponse(returnDictChangeToLanguage(newfriendship.data, lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable()
    def destroy(self, request, *args, **kwargs):
        try:
            lang = request.GET.get('lang')
            instance = self.get_object()
            if request.user.has_perm('usersys.admin_deletefriend'):
                pass
            elif request.user == instance.user or request.user == instance.friend:
                pass
            else:
                raise InvestError(code=2009)
            with transaction.atomic():
                instance.is_deleted = True
                instance.deleteduser = request.user
                instance.deletedtime = datetime.datetime.now()
                instance.save()
                return JSONResponse(SuccessResponse(returnDictChangeToLanguage(UserFriendshipUpdateSerializer(instance).data, lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))



@api_view(['POST'])
def login(request):
    """用户登录 """
    try:
        receive = request.data
        lang = request.GET.get('lang')
        clienttype = request.META.get('HTTP_CLIENTTYPE')
        username = receive['account']
        password = receive['password']
        source = receive.pop('datasource', None)
        if source:
            datasource = DataSource.objects.filter(id=source, is_deleted=False)
            if datasource.exists():
                userdatasource = datasource.first()
            else:
                raise InvestError(code=8888)
        else:
            raise InvestError(code=8888, msg='datasource field is required')
        if not username or not password or not userdatasource:
            raise InvestError(code=20071,msg='参数不全')
        user = auth.authenticate(username=username, password=password, datasource=userdatasource)
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
        return JSONResponse(SuccessResponse(returnDictChangeToLanguage(response,lang)))
    except InvestError as err:
        return JSONResponse(InvestErrorResponse(err))
    except Exception:
        catchexcption(request)
        return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))



