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

from usersys.models import MyUser, MyToken, UserRelation
from usersys.serializer import UserSerializer, UserListSerializer,UserRelationSerializer
from utils.util import read_from_cache, write_to_cache, JSONResponse, catchexcption, loginTokenIsAvailable


class UserView(viewsets.ModelViewSet):
    filter_backends = (filters.SearchFilter,filters.DjangoFilterBackend,)
    # permission_classes = (IsAuthenticated,)
    # queryset = MyUser.objects.filter(is_active=True).order_by('-id')
    filter_fields = ('phone','email','name','id','groups','trader','usertype')
    search_fields = ('phone','email','name','id','org__id','trader')
    serializer_class = UserListSerializer

    def get_queryset(self):
        """
        This view should return a list of all the purchases
        for the currently authenticated user.
        """
        users = read_from_cache('users')
        if users:
            return users
        else:
            users = MyUser.objects.order_by('id')
            write_to_cache('users', users)
            readusers = read_from_cache('users')
            return readusers
        # user = self.request.user
        # return MyUser.objects.filter(trader_id=user)


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
            phone = data['phone']
            userstatu = data.get('userstatu')
            usertype = data['usertype']
            if not request.user.is_superuser:
                userstatu = 1
            try:
                user = self.get_queryset().get(phone=phone)
            except MyUser.DoesNotExist:
                group = Group.objects.get(id=usertype)
                user = MyUser()
                user.name = username
                user.set_password(password)
                user.email = email
                user.phone = phone
                user.usertype = usertype
                user.userstatu = userstatu
                if usertype == 1 and data.get('trader'):
                    user.trader_id = data['trader']
                user.save()
                user.groups.add(group)
                user.save()
                response = {
                    'result': UserSerializer(user).data,
                    'error': None,
                }
                return JSONResponse(response)
            else:
                response = {
                    'result': None,
                    'error': 'user with this phone already exists.',
                }
                return JSONResponse(response)
        except Exception:
            catchexcption(request)
            response = {
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
                'result': serializer.data,
                'error': None,
            }
            return JSONResponse(response)
        except Exception:
            catchexcption(request)
            response = {
                'result': None,
                'error': traceback.format_exc().split('\n')[-2],
            }
            return JSONResponse(response)


    #put
    @loginTokenIsAvailable()
    def update(self, request, *args, **kwargs):
        try:
            token = MyToken.objects.get(key=request.META.get('HTTP_TOKEN'))
            user = token.user
            if user == self.get_object() or user.is_superuser or user.has_perm('usersys.change_myuser'):
                pass
            else:
                response = {
                    'result': None,
                    'error': '没有权限',
                }
                return JSONResponse(response,status=status.HTTP_403_FORBIDDEN)
        except MyToken.DoesNotExist:
            response = {
                'result': None,
                'error': '没有权限',
            }
            return JSONResponse(response, status=status.HTTP_403_FORBIDDEN)

        try:
            user = self.get_object()
            data = request.data
            keylist = data.keys()
            for key in keylist:
                if hasattr(user, key):
                    # if key == 'userstatu':
                    #     setattr(user,'userstatu_id' , data[key])
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
            user.save(update_fields=keylist)
            newuser = self.get_object()
            serializer = UserSerializer(newuser)
            return JSONResponse(serializer.data)
        except MyUser.DoesNotExist:
            response = {
                'result': None,
                'error': 'user is not found.',
            }
            return JSONResponse(response)
        except Exception:
            catchexcption(request)
            response = {
                'result': None,
                'error': traceback.format_exc().split('\n')[-2],
            }
            return JSONResponse(response)


    #patch
    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    #delete     'is_active' == false
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



class UserRelationView(mixins.CreateModelMixin,
                       mixins.UpdateModelMixin,
                       mixins.DestroyModelMixin,
                       mixins.ListModelMixin,
                       GenericViewSet):
    filter_backends = (filters.SearchFilter, filters.DjangoFilterBackend,)
    # permission_classes = (AllowAny,)
    queryset = UserRelation.objects.order_by('id')
    filter_fields = ('investoruser', 'traderuser', 'relationtype')
    search_fields = ('investoruser', 'traderuser', 'relationtype')
    serializer_class = UserRelationSerializer

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
            relationtype = request.data['relationtype']

            newinvestoruser = request.data['newinvestoruser']
            newtraderuser = request.data['newtraderuser']
            newrelationtype = request.data['newrelationtype']

            newrelation = self.get_queryset().get(investoruser=investoruser,traderuser=traderuser,relationtype=relationtype)
            newrelation.investoruser_id = newinvestoruser
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







@api_view(['POST'])
def login(request):
    receive = request.data
    if request.method == 'POST':
        username = receive['phone']
        password = receive['password']
        clienttype = request.META.get('HTTP_CLIENTTYPE')
        user = auth.authenticate(phone=username, password=password)
        if user is not None and user.is_active and clienttype:
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
                    MyUser.objects.get(phone=username)
                    cause = u'密码错误'
            except MyUser.DoesNotExist:
                cause = u'用户不存在'

            return JSONResponse({
                "result": 0,
                "cause":cause,
                })




def maketoken(user,clienttype):
    try:
        token = MyToken.objects.get(user=user, clienttype=clienttype)
    except MyToken.DoesNotExist:
        pass
    else:
        token.delete()
    token = MyToken.objects.create(user=user, clienttype=clienttype)
    serializer = UserSerializer(user)

    response = serializer.data
    return {'token':token.key,
        "user_info": response,  # response contain user_info and token
    }


