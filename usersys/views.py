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
from utils.util import read_from_cache, write_to_cache, loginTokenIsAvailable, JSONResponse,\
    permissiondeniedresponse, catchexcption, cache_delete_key


class UserView(viewsets.ModelViewSet):
    filter_backends = (filters.DjangoFilterBackend,)
    queryset = MyUser.objects.filter(is_deleted=False)
    filter_fields = ('mobile','email','name','id','groups','trader',)
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
    @transaction.atomic()
    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            mobilecode = data.pop('mobilecode', None)
            mobilecodetoken = data.pop('mobilecodetoken', None)
            mobile = data.get('mobile')
            email = data.get('email')
            try:
                mobileauthcode = MobileAuthCode.objects.get(mobile=mobile, code=mobilecode, token=mobilecodetoken)
            except MobileAuthCode.DoesNotExist:
                raise ValueError('手机验证码不匹配')
            else:
                if mobileauthcode.isexpired():
                    raise ValueError('验证码已过期')
            password = data.pop('password', None)
            try:
                self.queryset.get(Q(mobile=mobile) | Q(email=email))
            except MyUser.DoesNotExist:
                pass
            else:
                response = {'success': False, 'result': None, 'error': 'user with this mobile already exists.'}
                return JSONResponse(response)
            user = MyUser(email=email, mobile=mobile)
            user.set_password(password)
            user.save()
            keylist = data.keys()
            canCreateField = []
            cannoteditlist = [key for key in keylist if key not in canCreateField]
            if cannoteditlist:
                permissiondeniedresponse['error'] = '没有权限修改%s' % cannoteditlist
                return JSONResponse(permissiondeniedresponse)
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
        if request.user.has_perm('MyUserSys.admin_adduser'):
            canCreateField = []
        elif request.user.has_perm('MyUserSys.trader_adduser'):
            canCreateField = []
        else:
            return JSONResponse(permissiondeniedresponse)
        try:
            data = request.data
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
                permissiondeniedresponse['error'] = '没有权限修改%s' % cannoteditlist
                return JSONResponse(permissiondeniedresponse)
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

    # @loginTokenIsAvailable()
    @detail_route(methods=['get'])
    def getdetailinfo(self, request, *args, **kwargs):
        try:
            user = self.get_object()
            if request.user == user:
                userserializer = UserSerializer
            else:
                if request.user.has_perm('MyUserSys.as_admin'):
                    userserializer = UserSerializer
                elif request.user.has_perm('MyUserSys.trader_change', self.get_object()):
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
            canChangeField = []
            if request.user == user:
                canChangeField[0:0] = []
            else:
                if request.user.has_perm('usersys.admin_changeuser'):
                    canChangeField[0:0] = []
                elif request.user.has_perm('usersys.trader_changeuser',self.get_object()):
                    canChangeField[0:0] = []
                else:
                    return JSONResponse(permissiondeniedresponse)
        except:
            return JSONResponse({'success':False,'result': None,'error': traceback.format_exc().split('\n')[-2],})
        try:
            data = request.data
            keylist = data.keys()
            canCreateField = []
            cannoteditlist = [key for key in keylist if key not in canCreateField]
            if cannoteditlist:
                permissiondeniedresponse['error'] = '没有权限修改%s' % cannoteditlist
                return JSONResponse(permissiondeniedresponse)
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

    #delete     'is_active' == false
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
            user = self.queryset.get(mobile=mobile)
            user.set_password(password)
            user.save(update_fields=['password'])
            return JSONResponse({'success': True, 'result': password, 'error': None})
        except:
            return JSONResponse({'success': False, 'result': None, 'error': traceback.format_exc().split('\n')[-2],})

    @loginTokenIsAvailable()
    @detail_route(methods=['put'])
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
            user.set_password(password)
            user.save(update_fields=['password'])
            return JSONResponse({'success': True, 'result': password, 'error': None})
        except:
            return JSONResponse({'success': False, 'result': None, 'error': traceback.format_exc().split('\n')[-2],})

    # @loginTokenIsAvailable(['usersys.as_adminuser'])
    @detail_route(methods=['get'])
    def resetpassword(self,request, *args, **kwargs):
        try:
            user = self.get_object()
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

    @loginTokenIsAvailable(['MyUserSys.as_admin','MyUserSys.as_trader','MyUserSys.as_investor'])
    def list(self, request, *args, **kwargs):
        page_size = request.GET.get('page_size')
        page_index = request.GET.get('page_index')  #从第一页开始
        if not page_size:
            page_size = 10
        if not page_index:
            page_index = 1
        queryset = self.filter_queryset(self.get_queryset())
        if request.user.has_perm('MyUserSys.as_admin'):
            queryset = queryset
        elif request.user.has_perm('MyUserSys.as_trader'):
            queryset = queryset.filter(traderuser=request.user)
        elif request.user.has_perm('MyUserSys.as_investor'):
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


    @loginTokenIsAvailable(['MyUserSys.add_userrelation'])
    def create(self, request, *args, **kwargs):
        try:
            # data = {
            #     'investoruser':2,
            #     'traderuser':2,
            #     'relationtype':False,
            # }
            data = request.data
            if request.user.has_perm('MyUserSys.admin_adduserrelation'):
                pass
            elif request.user.has_perm('MyUserSys.add_userrelation'):
                data['traderuser'] = request.user.id
            else:
                raise ValueError('没有权限')
            data['createuser'] = request.user.id
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


    def retrieve(self, request, *args, **kwargs):
        try:
            userrelation = self.get_object()
            if request.user.has_perm('MyUserSys.as_admin'):
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

    # @loginTokenIsAvailable()
    def update(self, request, *args, **kwargs):
        try:
            data = request.data
            relation = self.get_object()
            if request.user.has_perm('MyUserSys.admin_changeuserrelation'):
                pass
            elif request.user.has_perm('MyUserSys.change_userrelation', relation):
                data['traderuser'] = request.user.id
                data.pop('relationtype', None)
            else:
                raise ('没有权限')
            data['lastmodifyuser'] = request.user.id
            data['lastmodifytime'] = datetime.datetime.now()
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

    @loginTokenIsAvailable(['MyUserSys.delete_userrelation'])
    def destroy(self, request, *args, **kwargs):
        try:
            userrelation = self.get_object()
            if request.user.has_perm('MyUserSys.delete_userrelation',userrelation):
                pass
            elif request.user.has_perm('MyUserSys.admin_deleteuserrelation'):
                pass
            else:
                raise ('没有权限')
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
        tokens = MyToken.objects.filter(user=user, clienttype__id=clienttype, is_deleted=False)
    except MyToken.DoesNotExist:
        pass
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

