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
from rest_framework import mixins
from rest_framework import status
from rest_framework import viewsets

from rest_framework.decorators import api_view, detail_route
from rest_framework.viewsets import GenericViewSet
from usersys.models import MyUser, MyToken, UserRelation, userTags, MobileAuthCode
from usersys.serializer import UserSerializer, UserListSerializer, UserRelationSerializer, UserTagsSerializer, \
    CreatUserSerializer
from sourcetype.models import ClientType, Tag
from utils.util import read_from_cache, write_to_cache, loginTokenIsAvailable, JSONResponse,\
    permissiondeniedresponse, catchexcption, cache_delete_key


class UserView(viewsets.ModelViewSet):
    filter_backends = (filters.SearchFilter,filters.DjangoFilterBackend,)
    queryset = MyUser.objects.filter(is_deleted=False).order_by('id')
    filter_fields = ('mobile','email','name','id','groups','trader',)
    search_fields = ('mobile','email','name','id','org__id','trader')
    serializer_class = UserListSerializer
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

    @loginTokenIsAvailable(['usersys.as_admin'])
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
        serializer = self.get_serializer(queryset, many=True)
        return JSONResponse({'success':True,'result': serializer.data,'error': None,})

    #注册用户(新注册用户没有交易师)
    @transaction.atomic()
    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            mobilecode = data.pop('mobilecode', None)
            mobilecodetoken = data.pop('mobilecodetoken', None)
            mobile = data.get('mobile')
            email = data.get('email')
            # try:
            #     mobileauthcode = MobileAuthCode.objects.get(mobile=mobile, code=mobilecode, token=mobilecodetoken)
            # except MobileAuthCode.DoesNotExist:
            #     raise ValueError('手机验证码不匹配')
            # else:
            #     if mobileauthcode.isexpired():
            #         raise ValueError('验证码已过期')
            password = data.pop('password', None)
            try:
                user = self.get_queryset().get(Q(mobile=mobile) | Q(email=email))
            except MyUser.DoesNotExist:
                pass
            else:
                response = {'success': False, 'result': None, 'error': 'user with this mobile already exists.'}
                return JSONResponse(response)
            user = MyUser(email=email, mobile=mobile)
            user.set_password(password)
            user.save()
            userser = CreatUserSerializer(user, data=data)
            if userser.is_valid():
                user = userser.save()
                # canCreateField = []
                keylist = data.keys()
                for key in keylist:
                    # if key not in canCreateField:
                    #     data.pop(key)
                    if key == 'tags':
                        usertaglist = data.pop(key)
                        taglist = []
                        for tag in usertaglist:
                            taglist.append({'tag': tag, 'user': user.pk, })
                        usertags = UserTagsSerializer(data=taglist, many=True)
                        if usertags.is_valid():
                            usertags.save()
                            # else:
                            #     permissiondeniedresponse['error'] = '没有权限修改 %s的%s' % (key, user.name)
                            #     return JSONResponse(permissiondeniedresponse)
            else:
                raise ValueError('err_%s' % userser.error_messages)
            return JSONResponse({'success': True, 'result': UserSerializer(user).data, 'error': None, })
        except Exception:
            catchexcption(request)
            return JSONResponse({'success': False, 'result': None, 'error': traceback.format_exc().split('\n')[-2]})

    #新增用户（可以有交易师）
    @transaction.atomic()
    @loginTokenIsAvailable()
    def adduser(self, request, *args, **kwargs):
        if request.user.has_perm('usersys.admin_add'):
            canCreateField = []
        elif request.user.has_perm('usersys.trader_add'):
            canCreateField = []
        else:
            return JSONResponse(permissiondeniedresponse)
        try:
            data = request.data
            password = data.get('password')
            email = data.get('email')
            mobile = data.get('mobile')
            try:
                user = self.get_queryset().filter(Q(mobile=mobile)|Q(email=email))
            except MyUser.DoesNotExist:
                pass
            else:
                return JSONResponse({'success':False,'result': None,'error': '用户已存在',})
            user = MyUser()
            user.set_password(password)
            user.save()
            keylist = data.keys()
            for key in keylist:
                if key in canCreateField:
                    if hasattr(user, key):
                        if key in ['org', 'trader','userstatu', 'title', 'school', 'profes', 'registersource']:
                            setattr(user, '%s_id' % key, data[key])
                        elif key == 'groups':
                            user.groups.add(Group.objects.get(id=data[key]))
                        elif key == 'tags':
                            usertaglist = []
                            for tag in Tag.objects.in_bulk(data[key]):
                                usertaglist.append(userTags(user=user, tag=tag, createuser=request.user))
                            user.user_tags.bulk_create(usertaglist)
                        else:
                            setattr(user, key, data[key])
                    else:
                        keylist.remove(key)
                else:
                    permissiondeniedresponse['error'] = '没有权限修改 %s的%s'
                    return JSONResponse(permissiondeniedresponse)
            user.createuser = request.user
            user.save()
            if request.user.has_perm('usersys.admin_add'):
                if 'trader' in keylist:
                    user.investor_relations.create(investoruser=user, traderuser_id=data['trader'], type=True)
            elif request.user.has_perm('usersys.trader_add'):
                user.trader = request.user
                user.investor_relations.create(investoruser=user, traderuser=request.user, type=True)
            return JSONResponse({'success':True,'result': UserSerializer(user).data,'error': None,})
        except Exception:
            catchexcption(request)
            return JSONResponse({'success':False,'result': None,'error': traceback.format_exc().split('\n')[-2],})


    #get
    @loginTokenIsAvailable()
    def retrieve(self, request, *args, **kwargs):
        try:
            user = self.get_object()
            if request.user == user:
                userserializer = UserSerializer
            else:
                if request.user.is_superuser:
                    userserializer = UserSerializer
                elif request.user.has_perm('usersys.as_admin'):
                    userserializer = UserSerializer
                elif request.user.has_perm('usersys.trader_change',self.get_object()):
                    userserializer = UserSerializer
                else:
                    return JSONResponse(permissiondeniedresponse)
            serializer = userserializer(user)
            return JSONResponse({'success':True,'result': serializer.data,'error': None})

        except Exception:
            catchexcption(request)
            return JSONResponse({'success':False,'result': None,'error': traceback.format_exc().split('\n')[-2],})


    #patch
    @loginTokenIsAvailable()
    def partial_update(self, request, *args, **kwargs):
        try:
            user = self.get_object()
            canChangeField = []
            if request.user == user:
                canChangeField[0:0] = []
            else:
                if request.user.has_perm('usersys.admin_change'):
                    canChangeField[0:0] = []
                elif request.user.has_perm('usersys.trader_change',self.get_object()):
                    canChangeField[0:0] = []
                else:
                    return JSONResponse(permissiondeniedresponse)
        except:
            return JSONResponse({'success':False,'result': None,'error': traceback.format_exc().split('\n')[-2],})
        try:
            data = request.data
            keylist = data.keys()
            for key in keylist:
                if key in canChangeField:
                    if hasattr(user, key):
                        if key in ['org','trader','userstatu','title','school','profes','registersource']:
                            setattr(user, '%s_id'%key, data[key])
                        elif key == 'groups':
                            user.groups.clear()
                            user.groups.add(Group.objects.get(id=data[key]))
                        elif key == 'tags':
                            taglist = Tag.objects.in_bulk(data[key])
                            addlist = [item for item in taglist if item not in user.tags.all()]
                            removelist = [item for item in user.tags.all() if item not in taglist]
                            user.user_tags.filter(tag__in=removelist).update(isdeleted=True,deletedtime=datetime.datetime.utcnow(),deletedUser=request.user)
                            usertaglist = []
                            for tag in addlist:
                               usertaglist.append(userTags(user=user,tag=tag,createuser=request.user))
                            user.user_tags.bulk_create(usertaglist)
                        else:
                            setattr(user,key,data[key])
                    else:
                        keylist.remove(key)
                else:
                    permissiondeniedresponse['error'] = '没有权限修改 %s的%s'% (key,user.name)
                    return JSONResponse(permissiondeniedresponse)
            user.save(update_fields=keylist)
            if request.user.has_perm('usersys.admin_add'):
                if 'trader' in keylist:
                    user.investor_relations.create(investoruser=user, traderuser_id=data['trader'], type=True)
            elif request.user.has_perm('usersys.trader_add'):
                user.trader = request.user
                user.investor_relations.create(investoruser=user, traderuser=request.user, type=True)
            cache_delete_key(self.redis_key+'_%s'%user.id)
            newuser = self.get_object()
            serializer = UserSerializer(newuser)
            return JSONResponse({'success':True,'result': serializer.data,'error':None})
        except Exception:
            catchexcption(request)
            return JSONResponse({'success':False,'result': None,'error': traceback.format_exc().split('\n')[-2]})

    #delete     'is_active' == false
    @loginTokenIsAvailable(['usersys.as_admin'])
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
        except:
            return JSONResponse({'success':False,'result': None,'error': traceback.format_exc().split('\n')[-2]})
        try:
            instance.is_deleted = False
            instance.deleteduser = request.user
            instance.deletedtime = datetime.datetime.utcnow()
            instance.save()
            return JSONResponse({'success':True,'result': None,'error':None})
        except:
            catchexcption(request)
            return JSONResponse({'success':False,'result': None,'error': traceback.format_exc().split('\n')[-2]})

    @detail_route()
    def getUserPermissions(self, request, *args, **kwargs):
        user = self.get_object()
        permissions = {}
        permissions['user_permissions'] = user.user_permissions.values()
        permissions['group_permissions'] = user.get_group_permissions()

        return JSONResponse({'success':True,'result': permissions,'error':None})

class UserRelationView(mixins.CreateModelMixin,
                       mixins.UpdateModelMixin,
                       mixins.DestroyModelMixin,
                       mixins.ListModelMixin,
                       GenericViewSet):
    filter_backends = (filters.SearchFilter, filters.DjangoFilterBackend,)
    # permission_classes = (AllowAny,)
    queryset = UserRelation.objects.filter(is_deleted=False)
    filter_fields = ('investoruser', 'traderuser', 'relationtype')
    search_fields = ('investoruser', 'traderuser', 'relationtype')
    serializer_class = UserRelationSerializer
    redis_key = 'usersrelation'
    Model = UserRelation

    def get_queryset(self):
        realtions = read_from_cache(self.redis_key)
        if realtions:
            return realtions
        else:
            realtions = self.Model.objects.all().order_by('id')
            write_to_cache(self.redis_key, realtions)
            readusers = read_from_cache(self.redis_key)
            return readusers

    @loginTokenIsAvailable(['usersys.as_admin','usersys.as_trader','usersys.as_investor'])
    def list(self, request, *args, **kwargs):
        page_size = request.GET.get('page_size')
        page_index = request.GET.get('page_index')  #从第一页开始
        if not page_size:
            page_size = 10
        if not page_index:
            page_index = 1
        queryset = self.filter_queryset(self.get_queryset())
        if request.user.has_perm('usersys.as_admin'):
            queryset = queryset
        elif request.user.has_perm('usersys.as_trader'):
            queryset = queryset.filter(traderuser=request.user)
        elif request.user.has_perm('usersys.as_investor'):
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

    @loginTokenIsAvailable(['usersys.add_userrelation'])
    def create(self, request, *args, **kwargs):
        try:
            investoruser = request.data['investoruser']
            traderuser = request.data['traderuser']
            relationtype = request.data['relationtype']
            newrelation = UserRelation()
            if not relationtype:
                pass
            else:
                investor = MyUser.objects.get(id=investoruser)
                investor.trader_id = traderuser
                investor.save()
            newrelation.investoruser_id = investoruser
            newrelation.traderuser_id = traderuser
            newrelation.relationtype = relationtype
            newrelation.createuser =request.user
            newrelation.save()
            cache_delete_key(self.redis_key)
            response = {'success':True,'result':'关系建立成功','error':None }
            return JSONResponse(response)
        except:
            catchexcption(request)
            response = {'success': False,'result': None,'error': traceback.format_exc().split('\n')[-2],}
            return JSONResponse(response)

    @loginTokenIsAvailable(['usersys.change_userrelation'])
    def update(self, request, *args, **kwargs):
        try:
            investoruser = request.data['investor']
            traderuser = request.data['trader']

            newtraderuser = request.data['newtrader']
            newrelationtype = request.data['newtype']

            if not newrelationtype:
                pass
            else:
                investor = MyUser.objects.get(id=investoruser)
                investor.trader_id = newtraderuser
                investor.save()
            relation = UserRelation.objects.get(investoruser_id=investoruser, traderuser_id=traderuser,is_deleted=False)
            relation.traderuser_id = newtraderuser
            relation.relationtype = newrelationtype
            relation.deletedUser = request.user
            relation.deletedtime = datetime.datetime.now()
            relation.save()
            cache_delete_key(self.redis_key)
            response = {
                'success': True,
                'result':'修改成功',
                'error':None
            }
            return JSONResponse(response,status=status.HTTP_201_CREATED)
        except:
            transaction.rollback()
            catchexcption(request)
            response = {
                'success': False,
                'result': None,
                'error': traceback.format_exc().split('\n')[-2],
            }
            return JSONResponse(response)

    @loginTokenIsAvailable(['usersys.delete_userrelation'])
    def destroy(self, request, *args, **kwargs):
        try:
            investoruser = request.data['investoruser']
            traderuser = request.data['traderuser']

            relation = self.get_queryset().get(investoruser=investoruser,traderuser=traderuser)
            relation.is_deleted = True
            relation.deletedUser = request.user
            relation.deletedtime = datetime.datetime.now()
            relation.save()
            cache_delete_key(self.redis_key)
            response = {
                'success': True,
                'result':'删除成功',
                'error':None
            }
            return JSONResponse(response,status=status.HTTP_201_CREATED)
        except:
            transaction.rollback()
            catchexcption(request)
            response = {
                'success': False,
                'result': None,
                'error': traceback.format_exc().split('\n')[-2],
            }
            return JSONResponse(response)



@api_view(['POST'])
def login(request):
    receive = request.data
    if request.method == 'POST':
        username = receive['mobile']
        password = receive['password']
        clienttype = request.META.get('HTTP_CLIENTTYPE')
        user = auth.authenticate(mobile=username, password=password)
        if user is not None and user.is_active and clienttype not in [1,2,3,4,5]:
            # update the token
            response = maketoken(user,clienttype)
            return JSONResponse({
                "result": 1,
                "user_info":response, # response contain user_info and token
                })
        else:
            try:
                if clienttype is None:
                    cause = u'登录类型不可用'
                else:
                    MyUser.objects.get(mobile=username)
                    cause = u'密码错误'
            except MyUser.DoesNotExist:
                cause = u'用户不存在'

            return JSONResponse({
                "result": 0,
                "message":cause,
                })


def maketoken(user,clienttype):
    try:
        tokens = MyToken.objects.filter(user=user, clienttype__id=clienttype, isdeleted=False)
    except MyToken.DoesNotExist:
        pass
    else:
        for token in tokens:
            token.isdeleted = True
            token.save(update_fields=['isdeleted'])
    type = ClientType.objects.get(id=clienttype)
    token = MyToken.objects.create(user=user, clienttype=type)
    serializer = UserListSerializer(user)
    response = serializer.data
    return {'token':token.key,
        "user_info": response,  # response contain user_info and token
    }

def add_or_change_strongrelate(investor,trader):
    try:
        relate = UserRelation.objects.get(investoruser__id=investor,relationtype=True)
        relate.traderuser_id = trader
    except UserRelation.DoesNotExist:
        relate = UserRelation()
        relate.investoruser_id = investor
        relate.traderuser_id = trader
        relate.relationtype = True
    relate.save()

