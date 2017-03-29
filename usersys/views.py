#coding=utf-8
import traceback
from django.contrib import auth
from django.contrib.auth.models import Group
from django.core.paginator import Paginator, EmptyPage
from django.db import transaction
from rest_framework import filters
from rest_framework import mixins
from rest_framework import status
from rest_framework import viewsets

from rest_framework.decorators import api_view, detail_route
from rest_framework.viewsets import GenericViewSet

from types.models import ClientType
from usersys.models import MyUser, MyToken, UserRelation, MobileAuthCode
from usersys.serializer import UserSerializer, UserListSerializer,UserRelationSerializer, UserCommenSerializer
from utils.perimissionfields import userpermfield
from utils.util import read_from_cache, write_to_cache, JSONResponse, catchexcption, loginTokenIsAvailable, \
    permissiondeniedresponse


class UserView(viewsets.ModelViewSet):
    filter_backends = (filters.SearchFilter,filters.DjangoFilterBackend,)
    # permission_classes = (IsAuthenticated,)
    # queryset = MyUser.objects.filter(is_active=True).order_by('-id')
    filter_fields = ('mobile','email','name','id','groups','trader','usertype')
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
        obj = read_from_cache(self.redis_key + '_%s' % self.kwargs[lookup_url_kwarg])
        if not obj:
            obj = self.Model.objects.get(id=self.kwargs[lookup_url_kwarg])
            write_to_cache(self.redis_key + '_%s' % self.kwargs[lookup_url_kwarg], obj)
        self.check_object_permissions(self.request, obj)
        return obj

    def get_queryset(self):
        users = read_from_cache(self.redis_key)
        if users:
            return users
        else:
            users = self.Model.objects.all().order_by('id')
            write_to_cache(self.redis_key, users)
            readusers = read_from_cache(self.redis_key)
            return readusers


    def list(self, request, *args, **kwargs):
        page_size = request.GET.get('page_size')    #每页10条数据
        page_index = request.GET.get('page_index')  #从第一页开始
        if not page_size:
            page_size = 10
        if not page_index:
            page_index = 1
        queryset = self.filter_queryset(self.get_queryset())
        try:
            queryset = Paginator(queryset, page_size)
        except EmptyPage:
            return JSONResponse({'success':True,'result':None,'count':0})
        queryset = queryset.page(page_index)
        serializer = self.get_serializer(queryset, many=True)
        return JSONResponse({'success':True,'result':serializer.data,'count':len(serializer.data)})



    @transaction.atomic()
    # @loginTokenIsAvailable()
    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            username = data['name']
            password = data['password']
            email = data['email']
            mobile = data['mobile']
            userstatu = data.get('userstatu')
            usertype = data['usertype']
            if not request.user.is_superuser:
                userstatu = 1
            try:
                user = self.get_queryset().get(mobile=mobile)
            except MyUser.DoesNotExist:
                group = Group.objects.get(id=usertype)
                user = MyUser()
                user.name = username
                user.set_password(password)
                user.email = email
                user.mobile = mobile
                user.usertype = usertype
                user.userstatu = userstatu
                if usertype == 1 and data.get('trader'):
                    user.trader_id = data['trader']
                user.save()
                user.groups.add(group)
                user.save()
                response = {
                    'success':True,
                    'result': UserSerializer(user).data,
                    'error': None,
                }
                return JSONResponse(response)
            else:
                response = {
                    'success':False,
                    'result': None,
                    'error': 'user with this mobile already exists.',
                }
                return JSONResponse(response)
        except Exception:
            catchexcption(request)
            response = {
                'success': False,
                'result': None,
                'error': traceback.format_exc().split('\n')[-2],
            }
            return JSONResponse(response)



    #get
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            response = {
                'success': True,
                'result': serializer.data,
                'error': None,
            }
            return JSONResponse(response)
        except Exception:
            catchexcption(request)
            response = {
                'success': False,
                'result': None,
                'error': traceback.format_exc().split('\n')[-2],
            }
            return JSONResponse(response)


    #put
    @transaction.atomic()
    @loginTokenIsAvailable(['MyUserSys.change_myuser', 'MyUserSys.change_otheruser'])
    def update(self, request, *args, **kwargs):
        permissions = kwargs['permissions']
        canChangeField = []
        if not permissions:
            return JSONResponse(permissiondeniedresponse)
        if 'usersys.change_myuser' in permissions:
            canChangeField[0:0] = userpermfield['usersys.change_myuser']
        if 'usersys.change_otheruser' in permissions:
            canChangeField[0:0] = userpermfield['usersys.change_otheruser']
        if request.user == self.get_object():
            canChangeField[len(canChangeField):len(canChangeField)] = []
        try:
            user = self.get_object()
            data = request.data
            keylist = data.keys()
            for key in keylist:
                if key in canChangeField:
                    if hasattr(user, key):
                        if key == 'org':
                            setattr(user, 'org_id', data[key])
                        elif key == 'trader':
                            if user.usertype == 1 and data['usertype'] == 1:
                                setattr(user, 'trader_id', data[key])
                            else:
                                keylist.remove(key)
                        elif key == 'usertype' or key == 'groups':
                            keylist.remove(key)
                        else:
                            setattr(user,key,data[key])
                    else:
                        keylist.remove(key)
                else:
                    permissiondeniedresponse['error'] = '没有权限修改 %s' % key
                    return JSONResponse(permissiondeniedresponse)
            user.save(update_fields=keylist)
            newuser = self.get_object()
            if 'trader' in keylist:
                relate = UserRelation.objects.get(investoruser=newuser,relationtype=True)
                add_or_change_strongrelate(user.id,data['trader'])
            serializer = UserSerializer(newuser)
            response = {
                'success': True,
                'result': serializer.data,
                'error': None,
            }
            return JSONResponse(response)
        except MyUser.DoesNotExist:
            response = {
                'success': False,
                'result': None,
                'error': 'user is not found.',
            }
            return JSONResponse(response)
        except Exception:
            catchexcption(request)
            response = {
                'success': False,
                'result': None,
                'error': traceback.format_exc().split('\n')[-2],
            }
            return JSONResponse(response)


    #patch
    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    #delete     'is_active' == false
    @transaction.atomic()
    def destroy(self, request, *args, **kwargs):
        try:
            user = self.get_object()
        except:
            response = {
                'result': None,
                'error': 'No MyUser matches the given query.',
            }
            return JSONResponse(response)
        else:
            user.delete()
            response = {
                'result': 'delete success',
                'error': None,
            }
            return JSONResponse(response,status=status.HTTP_204_NO_CONTENT)

    @loginTokenIsAvailable()
    @detail_route()
    def userBasicInfo(self,request,):
        try:
            instance = self.get_object()
            serializer = UserCommenSerializer(instance)
            response = {
                'success': True,
                'result': serializer.data,
                'error': None,
            }
            return JSONResponse(response)
        except Exception:
            catchexcption(request)
            response = {
                'success': False,
                'result': None,
                'error': traceback.format_exc().split('\n')[-2],
            }
            return JSONResponse(response)

    @loginTokenIsAvailable()
    @detail_route()
    def getUserPermissions(self, request, *args, **kwargs):
        try:
            user = self.get_object()
            permissions = {}
            permissions['user_permissions'] = user.user_permissions.values()
            permissions['group_permissions'] = user.get_group_permissions()
            return JSONResponse(permissions)
        except Exception:
            catchexcption(request)
            response = {
                'success': False,
                'result': None,
                'error': traceback.format_exc().split('\n')[-2],
            }
            return JSONResponse(response)

class UserRelationView(mixins.CreateModelMixin,
                       mixins.UpdateModelMixin,
                       mixins.DestroyModelMixin,
                       mixins.ListModelMixin,
                       GenericViewSet):
    filter_backends = (filters.SearchFilter, filters.DjangoFilterBackend,)
    # permission_classes = (AllowAny,)
    filter_fields = ('investoruser', 'traderuser', 'relationtype')
    search_fields = ('investoruser', 'traderuser', 'relationtype')
    serializer_class = UserRelationSerializer
    redis_key = 'UserRelation'
    Model = UserRelation

    def get_object(self):
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        assert lookup_url_kwarg in self.kwargs, (
            'Expected view %s to be called with a URL keyword argument '
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            'attribute on the view correctly.' %
            (self.__class__.__name__, lookup_url_kwarg)
        )
        obj = read_from_cache(self.redis_key + '_%s' % self.kwargs[lookup_url_kwarg])
        if not obj:
            obj = self.Model.objects.get(id=self.kwargs[lookup_url_kwarg])
            write_to_cache(self.redis_key + '_%s' % self.kwargs[lookup_url_kwarg], obj)
        self.check_object_permissions(self.request, obj)
        return obj

    def get_queryset(self):
        users = read_from_cache(self.redis_key)
        if users:
            return users
        else:
            users = self.Model.objects.all().order_by('id')
            write_to_cache(self.redis_key, users)
            readusers = read_from_cache(self.redis_key)
            return readusers

    def list(self, request, *args, **kwargs):
        page_size = request.GET.get('page_size')
        page_index = request.GET.get('page_index')  #从第一页开始
        if not page_size:
            page_size = 10
        if not page_index:
            page_index = 1
        queryset = self.filter_queryset(self.get_queryset())
        try:
            queryset = Paginator(queryset, page_size)
        except EmptyPage:
            return JSONResponse({'success':True,'result':None,'count':0})
        queryset = queryset.page(page_index)
        serializer = self.get_serializer(queryset, many=True)
        return JSONResponse({'success':True,'result':serializer.data,'count':len(serializer.data)})

    @transaction.atomic()
    def create(self, request, *args, **kwargs):
        # token = MyToken.objects.get(key=request.META.get('HTTP_TOKEN'))
        # if token.user == self.get_object() or token.user.is_superuser or token.user.has_perm('usersys.change_myuser'):
        #     pass
        # else:
        #     response = {
        #         'result': None,
        #         'error': '没有权限',
        #     }
        #     return JSONResponse(response,status=status.HTTP_403_FORBIDDEN)
        try:
            investoruser = request.data['investoruser']
            traderuser = request.data['traderuser']
            relationtype = request.data['relationtype']
            newrelation = UserRelation()
            newrelation.investoruser_id = investoruser
            newrelation.traderuser_id = traderuser
            newrelation.relationtype = relationtype
            newrelation.save({'add':True})
            if not newrelation.relationtype:
                pass
            else:
                investor = MyUser.objects.get(id=investoruser)
                investor.trader_id = traderuser
                investor.save(update_fields=['trader'])
            response = {
                'result':'关系建立成功',
                'error':None
            }
            return JSONResponse(response,status=status.HTTP_201_CREATED)
        except:
            catchexcption(request)
            response = {
                'result': None,
                'error': traceback.format_exc().split('\n')[-2],
            }
            return JSONResponse(response)

    @transaction.atomic()
    def update(self, request, *args, **kwargs):
        # token = MyToken.objects.get(key=request.META.get('HTTP_TOKEN'))
        # if token.user == self.get_object() or token.user.is_superuser or token.user.has_perm('usersys.change_myuser'):
        #     pass
        # else:
        #     response = {
        #         'result': None,
        #         'error': '没有权限',
        #     }
        #     return JSONResponse(response,status=status.HTTP_403_FORBIDDEN)
        try:
            investoruser = request.data['investoruser']
            traderuser = request.data['traderuser']
            newtraderuser = request.data['newtraderuser']
            newrelationtype = request.data['newrelationtype']

            if not newrelationtype:
                pass
            else:
                investoruser.trader_id = newtraderuser
                investoruser.save(update_fields=['trader'])
            newrelation = UserRelation.objects.get(investoruser=investoruser,traderuser=traderuser)
            newrelation.traderuser_id = newtraderuser
            newrelation.relationtype = newrelationtype
            newrelation.save(update_fields=['investoruser','traderuser','relationtype'])

            response = {
                'result':'修改成功',
                'error':None
            }
            return JSONResponse(response,status=status.HTTP_201_CREATED)
        except:
            transaction.rollback()
            catchexcption(request)
            response = {
                'result': None,
                'error': traceback.format_exc().split('\n')[-2],
            }
            return JSONResponse(response)

    @transaction.atomic()
    def destroy(self, request, *args, **kwargs):
        # token = MyToken.objects.get(key=request.META.get('HTTP_TOKEN'))
        # if token.user == self.get_object() or token.user.is_superuser or token.user.has_perm('usersys.change_myuser'):
        #     pass
        # else:
        #     response = {
        #         'result': None,
        #         'error': '没有权限',
        #     }
        #     return JSONResponse(response,status=status.HTTP_403_FORBIDDEN)
        try:
            investoruser = request.data['investoruser']
            traderuser = request.data['traderuser']

            newrelation = self.get_queryset().get(investoruser=investoruser,traderuser=traderuser)
            newrelation.delete()
            response = {
                'result':'删除成功',
                'error':None
            }
            return JSONResponse(response,status=status.HTTP_201_CREATED)
        except:
            transaction.rollback()
            catchexcption(request)
            response = {
                'result': None,
                'error': traceback.format_exc().split('\n')[-2],
            }
            return JSONResponse(response)






#登录
@api_view(['POST'])
def login(request):
    receive = request.data
    if request.method == 'POST':
        try:
            username = receive['mobile']
            email = None
        except:
            email = receive['email']
            username = None
        password = receive['password']
        clienttype = request.META.get('HTTP_CLIENTTYPE')
        user = auth.authenticate(mobile=username, password=password,email=email)
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
                "cause":cause,
                })

#生成token
def maketoken(user,clienttype):
    try:
        tokens = MyToken.objects.filter(user=user, clienttype__id=clienttype, isdeleted=False)
    except MyToken.DoesNotExist:
        pass
    else:
        for token in tokens:
            token.isdeleted = True
            token.save(update_fields=['isdeleted'])
            print token.timeout()

    type = ClientType.objects.get(id=clienttype)
    token = MyToken.objects.create(user=user, clienttype=type)

    serializer = UserSerializer(user)

    response = serializer.data
    return {'token':token.key,
        "user_info": response,  # response contain user_info and token
    }

#找回密码
@api_view(['POST'])
def lookbackpassword(request):
    receive = request.data
    if request.method == 'POST':
        mobile = receive['mobile']
        token = receive['token']
        code = receive['code']
        password = receive['password']
        user = MyUser.objects.get(mobile=mobile)
        if user:
            try:
                mobcode = MobileAuthCode.objects.get(mobile=mobile,token=token,code=code)
            except MobileAuthCode.DoesNotExist:
                return JSONResponse({
                "result": 0,
                "cause": '验证码有误',
            })
            else:
                if mobcode.isexpired:
                    return JSONResponse({
                        "result": 0,
                        "cause": '超过10分钟，验证码已过期',
                    })
                else:
                    user.set_password(password)
                    user.save()
                    userser = UserSerializer(user)
                    return JSONResponse({
                        "result": 1,
                        "user_info": userser,
                    })
        else:
            return JSONResponse({
                "result": 0,
                "cause": '该用户不存在',
            })

#修改投资人和交易师的评分
def change_relation_score(pk,score):
    relation = UserRelation.objects.get(pk=pk)
    if relation.score > score:
        pass
    else:
        relation.score = score
        relation.save()
    return relation.score


#新增或修改强关系交易师
def add_or_change_strongrelate(investor,trader):
    try:
        relate = UserRelation.objects.get(investoruser__id=investor,relationtype=True)
        relate.traderuser__id = trader
    except UserRelation.DoesNotExist:
        relate = UserRelation()
        relate.investoruser_id = investor
        relate.traderuser_id = trader
        relate.relationtype = True
    relate.save()

#检查手机号或者邮箱是否存在
def checkMobileOrEmailExist(request):
    data = request.data
    email = data['account']
    try:
        email_name, domain_part = email.strip().rsplit('@', 1)
    except ValueError:
        email = None
    else:
        email = '@'.join([email_name, domain_part.lower()])
    if email:
        filter_field = {'email':data['account']}
    else:
        filter_field = {'mobile':data['account']}
    try:
        user = MyUser.objects.get(**filter_field)
        serializeruser = UserCommenSerializer(user)

    except MyUser.DoesNotExist:
        return JSONResponse({'result':False, 'userbasic':None})
    else:
        return JSONResponse({'result':True, 'userbasic':serializeruser})



