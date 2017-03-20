#coding=utf-8

from django.db import transaction
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.views import APIView

from proj.models import project, finance, favorite
from proj.serializer import ProjSerializer, FavoriteSerializer
from usersys.models import MyUser
from utils.util import JSONResponse, catchexcption


class projlist(APIView):
    def get(self, request):
        allproj = project.objects.all()
        serializer = ProjSerializer(allproj,many=True)
        return JSONResponse({'result':serializer.data,'success':True,'error':None}, status=status.HTTP_200_OK)

    def post(self, request):
        # if not (request.user.is_authenticated() and request.user.has_perm('usersys.add_myuser')):
        #     return HttpResponse("没有权限",status=status.HTTP_403_FORBIDDEN)
        try:
            dic = request.data
            financemodel = finance.objects.create(dic['finance'])
            projstatu = dic['projStatuid']
            supportuser = MyUser.objects.get(count=dic['supportUserid'])
            proj = project.objects.create(title=dic['title'],statu=projstatu,supportuser=supportuser,description=dic['description'],finance=financemodel)
            proj.save()
            serializer = ProjSerializer(proj)
        except:
            return JSONResponse({'result':'add failed', 'success': False, 'error': None}, status=status.HTTP_400_BAD_REQUEST)
        return JSONResponse({'result':serializer.data, 'success': True, 'error': serializer.errors},
                                status=status.HTTP_200_OK)




        # if serializer.is_valid():
            # serializer.save()
            # return JSONResponse({'result':serializer.data,'success':True,'error':None}, status=status.HTTP_200_OK)
        # return JSONResponse({'result':None,'success':False,'error':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class projdetail(APIView):
    def get(self,request,pk):
        try:
            proj = project.objects.get(pk=pk)
        except project.DoesNotExist:
            return JSONResponse({'result':None,'success':False,'error':'not found'},status=status.HTTP_404_NOT_FOUND)
        else:
            serializer = ProjSerializer(proj)
            return JSONResponse({'result':serializer.data,'success':True,'error':None},status=status.HTTP_200_OK)

    def put(self,request,pk):
        try:
            proj = project.objects.get(pk=pk)
        except project.DoesNotExist:
            return JSONResponse({'result':None,'success':False,'error':'not found'},status=status.HTTP_404_NOT_FOUND)
        else:
            serializer = ProjSerializer(proj,data=request.data)
            if serializer.is_valid():
                serializer.save()
                return JSONResponse({'result':serializer.data,'success':True,'error':None}, status=status.HTTP_200_OK)
            return JSONResponse({'result':None,'success':False,'error':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request,pk):
        # if not (request.user.is_authenticated() and request.user.has_perm('usersys.add_myuser')):
        #     return HttpResponse("没有权限",status=status.HTTP_403_FORBIDDEN)
        try:
            proj = project.objects.get(pk=pk)
        except project.DoesNotExist:
            return JSONResponse({'result':None,'success':False,'error':'not found'},status=status.HTTP_404_NOT_FOUND)
        else:
            data = request.data
            list = data.keys()
            for key in list:
                if hasattr(proj,key):
                    # if key == 'author':
                    #     setattr(proj,'author_id' , data[key])
                    # else:
                        setattr(proj,key,data[key])
            proj.save(update_fields=list)
            serializer = ProjSerializer(proj)
            try:
                if serializer.is_valid():
                    proj.save(update_fields=list)
                    # transaction.commit()
            except:
                # transaction.rollback()
                return JSONResponse({'result':None,'success':False,'error':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return JSONResponse({'result':serializer.data,'success':True,'error':None}, status=status.HTTP_200_OK)
    def delete(self, request,pk):
        # if not (request.user.is_authenticated() and request.user.has_perm('usersys.add_myuser')):
        #     return HttpResponse("没有权限",status=status.HTTP_403_FORBIDDEN)
        try:
            proj = project.objects.get(pk=pk)
        except project.DoesNotExist:
            return JSONResponse({'result':None,'success':False,'error':'not found'},status=status.HTTP_404_NOT_FOUND)
        else:
            try:
                proj.delete()
                transaction.commit()
            except :
                transaction.rollback()
                return JSONResponse({'result': 'delete failed', 'success': False, 'error': 'HTTP_400_BAD_REQUEST'},
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                return JSONResponse({'result':'delete success','success':True,'error':None},status=status.HTTP_200_OK)

@api_view(['GET','POST'])
def allfavorite(request):
    '''
    List all favorite, or create a new favorite.
    '''
    if request.method == 'GET':
        header = request.META
        # if not (request.user.is_authenticated() and request.user.has_perm('usersys.add_myuser')):
        #     return HttpResponse("没有权限",status=status.HTTP_403_FORBIDDEN)
        userid = request.GET.get('userid')
        projid = request.GET.get('projid')
        typeid = request.GET.get('typeid')
        tasks = favorite.objects.all()
        if userid:
            tasks = tasks.filter(user_id=userid)
        if projid:
            tasks = tasks.filter(proj_id=projid)
        if typeid:
            tasks = tasks.filter(favoritetype_id=typeid)
        try:
            # tasks = Paginator(tasks,2)   #page_size  每页多少条数据
            # tasks = tasks.page(1)       #page_index 第几页
            serializer = FavoriteSerializer(tasks, many=True)
            return JSONResponse({'result': serializer.data,'success':True,'error':None}, content_type='application/json; charset=utf-8')
        except Exception as msg:
            catchexcption(request)
            return JSONResponse({'result': None, 'success': False, 'error': repr(msg)},
                                    status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'POST':



        data = request.data
        try:
            with transaction.atomic():
                proj = project.objects.get(id=data['projId'])
                user = MyUser.objects.get(count=data['userId'])
                favoriteType = data['favoriteType']
                favoriteobj = favorite.objects.create(proj=proj,user=user,favoritetype=favoriteType)
                favoriteobj.save()
                favor = favorite.objects.get(proj=proj,user=user,favoritetype=favoriteType)
                serializer = FavoriteSerializer(favor)
                return JSONResponse({'result': serializer.data,'success':True,'error':None},status=status.HTTP_200_OK)
        except Exception as exc:
            catchexcption(request)
            return JSONResponse({'result': None, 'success': False, 'error':repr(exc)},
                                status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET', 'PUT', 'DELETE','PATCH'])
def favoritetype(request, pk):
    try:
        task = favorite.objects.get(pk=pk)
    except favorite.DoesNotExist:
        catchexcption(request)
        return JSONResponse({'result':None,'success':False,'error':'not found'},status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = FavoriteSerializer(task)
        return JSONResponse({'result': serializer.data,'success':True,'error':None})
    elif request.method == 'PUT':
        serializer = FavoriteSerializer(task, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JSONResponse({'result': serializer.data,'success':True,'error':None})
        else:
            return JSONResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        task.delete()
        return JSONResponse(status=status.HTTP_204_NO_CONTENT)
    elif request.method == 'PATCH':
        data = request.data
        list = data.keys()
        for key in list:
            if hasattr(task,key):
                if key == 'author':
                    setattr(task,'author_id' , data[key])
                else:
                    setattr(task,key,data[key])
        task.save(update_fields=list)
        serializer = FavoriteSerializer(task)
        return JSONResponse({'result': serializer.data,'success':True,'error':None})