#coding=utf-8
import traceback

import datetime


from django.contrib import auth
from django.contrib.auth.models import Group, Permission
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

from APIlog.views import logininlog, apilog
from org.models import organization
from third.models import MobileAuthCode
from usersys.models import MyUser,UserRelation, userTags, UserFriendship
from usersys.serializer import UserSerializer, UserListSerializer, UserRelationSerializer,\
    CreatUserSerializer , UserCommenSerializer , UserRelationDetailSerializer, UserFriendshipSerializer, \
    UserFriendshipDetailSerializer, UserFriendshipUpdateSerializer, UserInvestorRelationSerializer, \
    UserTraderRelationSerializer, GroupSerializer, GroupDetailSerializer, GroupCreateSerializer, PermissionSerializer, \
    UpdateUserSerializer
from sourcetype.models import Tag, DataSource
from utils import perimissionfields
from utils.customClass import JSONResponse, InvestError, RelationFilter
from utils.sendMessage import sendmessage_userauditstatuchange, sendmessage_userregister, sendmessage_traderchange, \
    sendmessage_usermakefriends
from utils.util import read_from_cache, write_to_cache, loginTokenIsAvailable,\
    catchexcption, cache_delete_key, maketoken, returnDictChangeToLanguage, returnListChangeToLanguage, SuccessResponse, \
    InvestErrorResponse, ExceptionResponse, setrequestuser, getmenulist
from django_filters import FilterSet


class UserFilter(FilterSet):
    groups = RelationFilter(filterstr='groups', lookup_method='in')
    org = RelationFilter(filterstr='org',lookup_method='in')
    tags = RelationFilter(filterstr='tags',lookup_method='in',relationName='user_usertags__is_deleted')
    userstatus = RelationFilter(filterstr='userstatus',lookup_method='in')
    currency = RelationFilter(filterstr='org__currency', lookup_method='in')
    orgtransactionphases = RelationFilter(filterstr='org__orgtransactionphase', lookup_method='in',relationName='org__org_orgTransactionPhases__is_deleted')
    class Meta:
        model = MyUser
        fields = ('groups','org','tags','userstatus','currency','orgtransactionphases')


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
    filter_backends = (filters.SearchFilter,filters.DjangoFilterBackend,)
    queryset = MyUser.objects.filter(is_deleted=False)
    search_fields = ('mobile','email','usernameC','usernameE','org__orgnameC')
    serializer_class = UserSerializer
    filter_class = UserFilter
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
                serializerclass = UserListSerializer
            else:
                serializerclass = UserCommenSerializer
            count = queryset.count()
            try:
                queryset = Paginator(queryset, page_size)
            except EmptyPage:
                raise InvestError(code=1001)
            queryset = queryset.page(page_index)
            actionlist = {'get': False, 'change': False, 'delete': False}
            responselist = []
            for instance in queryset:
                if request.user.is_anonymous:
                    pass
                else:
                    if request.user.has_perm('usersys.admin_getuser') or request.user.has_perm('usersys.user_getuserlist'):
                        actionlist['get'] = True
                    if request.user.has_perm('usersys.admin_changeuser') or request.user.has_perm('usersys.user_changeuser',
                                                                                             instance):
                        actionlist['change'] = True
                    if request.user.has_perm('usersys.admin_deleteuser') or request.user.has_perm('usersys.user_deleteuser',
                                                                                             instance):
                        actionlist['delete'] = True
                instancedata = serializerclass(instance).data
                instancedata['action'] = actionlist
                responselist.append(instancedata)
            return JSONResponse(
                SuccessResponse({'count': count, 'data': returnListChangeToLanguage(responselist, lang)}))
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
                source = request.META.get('HTTP_SOURCE')
                if source:
                    datasource = DataSource.objects.filter(id=source,is_deleted=False)
                    if datasource.exists():
                        userdatasource = datasource.first()
                    else:
                        raise  InvestError(code=8888)
                else:
                    raise InvestError(code=8888,msg='source field is required,//forbidden')
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
                groupid = data.pop('groups', None)
                if not groupid:
                    raise InvestError(code=2007,msg='groups cannot be null')
                try:
                    Group.objects.get(id=groupid,datasource=userdatasource)
                except Exception:
                    raise InvestError(code=2007,msg='groups bust be an available GroupID')
                data['groups'] = [groupid]
                orgname = data.pop('orgname', None)
                if orgname:
                    if lang == 'en':
                        field = 'orgnameE'
                        filters = Q(orgnameE=orgname)
                    else:
                        field = 'orgnameC'
                        filters = Q(orgnameC=orgname)
                    orgset = organization.objects.filter(filters,is_deleted=False,datasource=userdatasource)
                    if orgset.exists():
                        org = orgset.first()
                    else:
                        org = organization()
                        setattr(org,field,orgname)
                        org.datasource= userdatasource
                        org.orgstatus_id = 1
                        org.save()
                    data['org'] = org.id
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
                returndic = CreatUserSerializer(user).data
                sendmessage_userregister(user,user,['email'])
                apilog(request, 'MyUser', None, None, datasource=request.user.datasource_id)
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
        try:

            lang = request.GET.get('lang')
            if request.user.has_perm('usersys.admin_adduser'):
                canCreateField = perimissionfields.userpermfield['usersys.admin_adduser']
            elif request.user.has_perm('usersys.user_adduser'):
                canCreateField = perimissionfields.userpermfield['usersys.trader_adduser']
            else:
                raise InvestError(2009,msg='没有新增权限')
            with transaction.atomic():
                password = data.pop('password','Aa123456')
                email = data.get('email')
                mobile = data.get('mobile')
                if not email or not mobile:
                    raise InvestError(code=2007)
                if self.get_queryset().filter(Q(mobile=mobile) | Q(email=email)).exists():
                    raise InvestError(code=2004)
                # user = MyUser(usernameC=data.get('usernameC',None),usernameE=data.get('usernameE',None),datasource_id=request.user.datasource.id)
                # user.set_password(password)
                # user.save()
                keylist = data.keys()
                cannoteditlist = [key for key in keylist if key not in canCreateField]
                if cannoteditlist:
                    raise InvestError(code=2009,msg='没有权限修改%s' % cannoteditlist)
                data['createduser'] = request.user.id
                data['createdtime'] = datetime.datetime.now()
                data['datasource'] = request.user.datasource.id
                data['password'] = 'Aa123456'
                tags = data.pop('tags', None)
                userserializer = CreatUserSerializer(data=data)
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
                return JSONResponse(SuccessResponse(returnDictChangeToLanguage(UserSerializer(user).data,lang=lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    #get
    @loginTokenIsAvailable(['usersys.admin_getuser','usersys.user_getuserlist'])
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
            useridlist = request.data.get('userlist')
            data = request.data.get('userdata')
            userlist = []
            messagelist = []
            if not useridlist or not isinstance(useridlist,list):
                raise InvestError(2007,msg='expect a not null id list')
            with transaction.atomic():
                for userid in useridlist:
                    user = self.get_object(userid)
                    olduserdata = UserSerializer(user)
                    sendmsg = False
                    if request.user == user:
                        canChangeField = perimissionfields.userpermfield['changeself']
                    else:
                        if request.user.has_perm('usersys.admin_changeuser'):
                            canChangeField = perimissionfields.userpermfield['usersys.admin_changeuser']
                        elif request.user.has_perm('usersys.user_changeuser',user):
                            canChangeField = perimissionfields.userpermfield['usersys.trader_changeuser']
                        else:
                            raise InvestError(code=2009)
                    keylist = data.keys()
                    cannoteditlist = [key for key in keylist if key not in canChangeField]
                    if cannoteditlist:
                        raise InvestError(code=2009,msg='没有权限修改_%s' % cannoteditlist)
                    data['lastmodifyuser'] = request.user.id
                    data['lastmodifytime'] = datetime.datetime.now()
                    tags = data.pop('tags', None)
                    if data.get('userstatus',None) and user.userstatus_id != data.get('userstatus',None):
                        sendmsg = True
                    userserializer = UpdateUserSerializer(user, data=data)
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
                                usertaglist.append(userTags(user=user, tag_id=tag, createuser=request.user))
                            user.user_usertags.bulk_create(usertaglist)
                    else:
                        raise InvestError(code=20071,msg='userdata有误_%s\n%s' % (userserializer.error_messages, userserializer.errors))
                    newuserdata = UserSerializer(user)
                    apilog(request, 'MyUser', olduserdata.data, newuserdata.data, modelID=userid,
                           datasource=request.user.datasource_id)
                    userlist.append(newuserdata.data)
                    messagelist.append((user,sendmsg))
                for user,sendmsg in messagelist:
                    if sendmsg:
                        sendmessage_userauditstatuchange(user,user,['app','email','webmsg'],sender=request.user)

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
            useridlist = request.data.get('users')
            userlist = []
            lang = request.GET.get('lang')
            if not useridlist or not isinstance(useridlist,list):
                raise InvestError(code=20071,msg='except a not null user id list')
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
                        if link in ['investor_relations','trader_relations','investor_timelines','supportor_timelines','trader_timelines']:
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
                        else:
                            manager = getattr(instance, link, None)
                            if not manager:
                                continue
                            # one to one
                            if isinstance(manager, models.Model):
                                if hasattr(manager, 'is_deleted') and not manager.is_deleted:
                                    manager.is_deleted = True
                                    manager.save()
                                else:
                                    manager.delete()
                            else:
                                try:
                                    manager.model._meta.get_field('is_deleted')
                                    if manager.all().filter(is_deleted=False).count():
                                        manager.all().update(is_deleted=True)
                                except FieldDoesNotExist:
                                    if manager.all().count():
                                        manager.all().delete()
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
    filter_fields = ('investoruser', 'traderuser', 'relationtype')
    search_fields = ('investoruser__usernameC', 'investoruser__usernameE', 'traderuser__usernameC', 'traderuser__usernameE')
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

    @loginTokenIsAvailable(['usersys.admin_getuserrelation','usersys.user_getuserrelationlist'])
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
            if request.user.has_perm('usersys.admin_getuserrelation'):
                pass
            else:
                queryset = queryset.filter(Q(traderuser=request.user) | Q(investoruser=request.user))
            try:
                count = queryset.count()
                queryset = Paginator(queryset, page_size)
            except EmptyPage:
                raise InvestError(code=1001)
            queryset = queryset.page(page_index)
            serializer = UserRelationSerializer(queryset, many=True)
            return JSONResponse(SuccessResponse({'count':count,'data':returnListChangeToLanguage(serializer.data,lang)}))
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
                lang = request.GET.get('lang')
                relationidlist =  request.data['relationlist']
                if not isinstance(relationidlist,list) or not relationidlist:
                    raise InvestError(2007,msg='expect a not null relation id list')
                relationlist = self.get_queryset().in_bulk(relationidlist)
                newlist = []
                sendmessagelist = []
                for relation in relationlist:
                    sendmsg = False
                    data =  request.data['newdata']
                    data.pop('investoruser')
                    if data.get('traderuser',None) and data.get('traderuser') != relation.traderuser_id:
                        sendmsg = True
                    if request.user.has_perm('usersys.admin_changeuserrelation'):
                        pass
                    elif request.user.has_perm('usersys.user_changeuserrelation', relation):
                        data['traderuser'] = request.user.id
                        data.pop('relationtype', None)
                    else:
                        raise InvestError(code=2009,msg='没有权限')
                    data['lastmodifyuser'] = request.user.id
                    data['lastmodifytime'] = datetime.datetime.now()
                    newrelationseria = UserRelationSerializer(relation,data=data)
                    if newrelationseria.is_valid():
                        newrelation = newrelationseria.save()
                    else:
                        raise InvestError(code=20071,msg=newrelationseria.errors)
                    newlist.append(newrelationseria.data)
                    sendmessagelist.append((newrelation,sendmsg))
                for newrelation, sendmsg in sendmessagelist:
                    if sendmsg:
                        sendmessage_traderchange(newrelation, newrelation.investoruser,['email', 'app', 'sms', 'webmsg'], sender=request.user)
                return JSONResponse(SuccessResponse(returnListChangeToLanguage(newlist,lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable()
    def destroy(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                relationidlist = request.data.get('relationlist',None)
                if not isinstance(relationidlist,list) or not relationidlist:
                    raise InvestError(2007,msg='expect a not null relation id list')
                lang = request.GET.get('lang')
                relationlist = self.get_queryset().filter(id__in=relationidlist)
                returnlist = []
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
                    returnlist.append(userrelation.id)
                return JSONResponse(SuccessResponse(returnlist))
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
    serializer_class = UserFriendshipDetailSerializer

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
                count = queryset.count()
                queryset = Paginator(queryset, page_size)
            except EmptyPage:
                raise InvestError(code=1001)
            queryset = queryset.page(page_index)
            serializer = UserFriendshipSerializer(queryset, many=True)
            return JSONResponse(SuccessResponse({'count':count,'data':returnListChangeToLanguage(serializer.data,lang)}))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable()
    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            data['createuser'] = request.user.id
            data['datasource'] = 1
            friendlist = data.pop('friend',None)
            if not friendlist or not isinstance(friendlist,list):
                raise InvestError(code=20071,msg='\'friends\' need a not null list')
            lang = request.GET.get('lang')
            if request.user.has_perm('usersys.admin_addfriend'):
                pass
            else:
                data['user'] = request.user.id
                data['isaccept'] = False
                data['accepttime'] = None
            with transaction.atomic():
                newfriendlist = []
                sendmessagelist = []
                for friendid in friendlist:
                    data['friend'] = friendid
                    newfriendship = UserFriendshipDetailSerializer(data=data)
                    if newfriendship.is_valid():
                        newfriend = newfriendship.save()
                    else:
                        raise InvestError(code=20071,msg='%s'%newfriendship.errors)
                    newfriendlist.append(newfriendship.data)
                    sendmessagelist.append(newfriend)
                for friendship in sendmessagelist:
                    sendmessage_usermakefriends(friendship,friendship.friend,['app', 'webmsg', 'sms', 'email'],sender=request.user)
                return JSONResponse(SuccessResponse(returnListChangeToLanguage(newfriendlist,lang)))
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
                canChangeField = ['userallowgetfavoriteproj', 'friendallowgetfavoriteproj', 'isaccept']
            elif request.user == instance.user:
                canChangeField = ['userallowgetfavoriteproj']
            elif request.user == instance.friend:
                canChangeField = ['friendallowgetfavoriteproj']
            else:
                raise InvestError(code=2009)
            keylist = data.keys()
            cannoteditlist = [key for key in keylist if key not in canChangeField]
            if cannoteditlist:
                raise InvestError(code=2009, msg='没有权限修改_%s' % cannoteditlist)
            with transaction.atomic():
                sendmessage = False
                if instance.isaccept == False and bool(data.get('isaccept', None)):
                    sendmessage = True
                newfriendship = UserFriendshipUpdateSerializer(instance,data=data)
                if newfriendship.is_valid():
                    friendship = newfriendship.save()
                else:
                    raise InvestError(code=20071, msg='%s' % newfriendship.errors)
                if sendmessage:
                    sendmessage_usermakefriends(friendship, friendship.user, ['app', 'webmsg'], sender=request.user)
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



class GroupPermissionView(viewsets.ModelViewSet):
    """
    list:获取权限组列表
    create:新增权限组
    retrieve:查看权限组详情
    update:修改权限组信息
    delete:删除权限组
    """
    queryset = Group.objects.all()
    serializer_class = GroupDetailSerializer

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

    #未登录用户不能访问
    def get_object(self):
        lookup_url_kwarg = 'pk'
        try:
            obj = self.get_queryset().get(id=self.kwargs[lookup_url_kwarg])
        except Group.DoesNotExist:
            raise InvestError(code=5002)
        assert self.request.user.is_authenticated, (
            "user must be is_authenticated"
        )
        if obj.datasource != self.request.user.datasource:
            raise InvestError(code=8888, msg='资源非同源')
        return obj

    @loginTokenIsAvailable()
    def list(self, request, *args, **kwargs):
        try:
            if not request.user.is_superuser:
                raise InvestError(2009)
            page_size = request.GET.get('page_size')
            page_index = request.GET.get('page_index')
            if not page_size:
                page_size = 10
            if not page_index:
                page_index = 1
            queryset = self.filter_queryset(self.get_queryset())
            try:
                count = queryset.count()
                queryset = Paginator(queryset, page_size)
            except EmptyPage:
                raise InvestError(code=1001)
            queryset = queryset.page(page_index)
            serializer = GroupDetailSerializer(queryset, many=True)
            return JSONResponse(
                SuccessResponse({'count': count, 'data':serializer.data}))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable()
    def create(self, request, *args, **kwargs):
        try:
            if not request.user.is_superuser:
                raise InvestError(2009)
            data = request.data
            with transaction.atomic():
                data['datasource'] = request.user.datasource_id
                permissionsIdList = data.get('permissions',None)
                if not isinstance(permissionsIdList,list):
                    raise InvestError(2007,msg='permissions must be an ID list')
                groupserializer = GroupCreateSerializer(data=data)
                if groupserializer.is_valid():
                    newgroup = groupserializer.save()
                    permissions = Permission.objects.filter(id__in=permissionsIdList)
                    map(newgroup.permissions.add, permissions)
                else:
                    raise InvestError(code=20071, msg='%s' % groupserializer.errors)
                return JSONResponse(SuccessResponse(groupserializer.data))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable()
    def retrieve(self, request, *args, **kwargs):
        try:
            if not request.user.is_superuser:
                raise InvestError(2009)
            group = self.get_object()
            serializer = GroupDetailSerializer(group)
            return JSONResponse(SuccessResponse(serializer.data))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable()
    def update(self, request, *args, **kwargs):
        try:
            if not request.user.is_superuser:
                raise InvestError(2009)
            with transaction.atomic():
                group = self.get_object()
                data = request.data
                permissionsIdList = data.pop('permissions', None)
                if not isinstance(permissionsIdList, list):
                    raise InvestError(2007, msg='permissions must be an ID list')
                serializer = GroupSerializer(group,data=data)
                if serializer.is_valid():
                    newgroup = serializer.save()
                    permissions = Permission.objects.filter(id__in=permissionsIdList)
                    newgroup.permissions.clear()
                    map(newgroup.permissions.add,permissions)
                else:
                    raise InvestError(2007,msg='%s'%serializer.errors)
                return JSONResponse(SuccessResponse(serializer.data))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable()
    def destroy(self, request, *args, **kwargs):
        try:
            if not request.user.is_superuser:
                raise InvestError(2009)
            with transaction.atomic():
                group = self.get_object()
                groupuserset = MyUser.objects.filter(is_deleted=False,groups__in=[group])
                if groupuserset.exists():
                    raise InvestError(2008)
                else:
                    group.delete()
                return JSONResponse(SuccessResponse(GroupSerializer(group).data))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

class PermissionView(viewsets.ModelViewSet):
    """
    list:获取权限列表
    """
    queryset = Permission.objects.exclude(name__icontains='obj级别')
    serializer_class = PermissionSerializer

    @loginTokenIsAvailable()
    def list(self, request, *args, **kwargs):
        try:
            if not request.user.is_superuser:
                raise InvestError(2009)
            queryset = self.queryset
            serializer = self.serializer_class(queryset, many=True)
            return JSONResponse(SuccessResponse(serializer.data))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
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
        source = request.META.get('HTTP_SOURCE')
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
        if not user.is_active:
            user.is_active = True
        user.save()
        perimissions = user.get_all_permissions()
        menulist = getmenulist(user)
        response = maketoken(user, clienttype)
        response['permissions'] = perimissions
        response['menulist'] = menulist
        logininlog(loginaccount=username, logintypeid=clienttype, datasourceid=source,userid=user.id)
        return JSONResponse(SuccessResponse(returnDictChangeToLanguage(response,lang)))
    except InvestError as err:
        return JSONResponse(InvestErrorResponse(err))
    except Exception:
        catchexcption(request)
        return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))


def testsendmsg(request):
    # print datetime.datetime.now()
    # sendmessage_userauditstatuchange(MyUser.objects.get(id=8),MyUser.objects.get(id=8),['app'])
    # print datetime.datetime.now()
    with open('/Users/investarget/Desktop/django_server/qiniu_uploadprogress/5qC86JOd54m5546v5L+d5bel56iL77yI5YyX5LqsKeaciemZkOWFrOWPuOW3peWVhuaho+ahiOi1hOaWmS3miKrmraIyMDE2LTA3LTEyLnBkZi.moLzok53nibnnjq.kv53lt6XnqIvvvIjljJfkuqwp5pyJ6ZmQ5YWs5Y+45bel5ZWG5qGj5qGI6LWE5paZLeaIquatojIwMTYtMDctMTIucGRm', 'w') as f:
        import json
        json.dump('aaaa', f)
    return JSONResponse({'xxx':'sss'})