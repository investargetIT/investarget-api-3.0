import datetime
import traceback

from django.core.paginator import EmptyPage
from django.core.paginator import Paginator
from django.shortcuts import render

# Create your views here.
from rest_framework import filters
from rest_framework import viewsets

from APIlog.models import loginlog, userviewprojlog, APILog
from APIlog.serializer import APILogSerializer
from utils.customClass import JSONResponse, InvestError
from utils.util import SuccessResponse, InvestErrorResponse, ExceptionResponse


def logininlog(loginaccount,logintypeid,datasourceid,userid=None):
    if isinstance(logintypeid,str):
        logintypeid = int(logintypeid)
    loginlog(loginaccount=loginaccount,logintype=logintypeid,datasource=datasourceid,user=userid).save()

def viewprojlog(userid,projid,sourceid):
    userviewprojlog(user=userid,proj=projid,source=sourceid).save()

def apilog(request,modeltype,request_before,request_after,modelID=None,datasource=None,model_name=None):
    if request.META.has_key('HTTP_X_FORWARDED_FOR'):
        ip = request.META['HTTP_X_FORWARDED_FOR']
    else:
        ip = request.META['REMOTE_ADDR']
    url = request.get_full_path()
    method = request.method
    requestbody = request.data
    if request.user.is_anonymous:
        requestuser = None
        datasource = datasource
        requestuser_name = None
    else:
        requestuser = request.user.id
        requestuser_name = request.user.usernameC
        datasource = request.user.datasource_id
    APILog(IPaddress=ip,URL=url,method=method,requestbody=requestbody,requestuser_id=requestuser,requestuser_name=requestuser_name,
           modeltype=modeltype,model_id=modelID,model_name=model_name,request_before=request_before,request_after=request_after,datasource=datasource).save()





class APILogView(viewsets.ModelViewSet):
    queryset = APILog.objects.filter(is_deleted=False)
    serializer_class = APILogSerializer
    def list(self, request, *args, **kwargs):
        try:
            page_size = request.GET.get('page_size')
            page_index = request.GET.get('page_index')
            if not page_size:
                page_size = 10
            if not page_index:
                page_index = 1
            queryset = self.filter_queryset(self.get_queryset())
            count = queryset.count()
            try:
                queryset = Paginator(queryset, page_size)
            except EmptyPage:
                    raise InvestError(code=1001)
            queryset = queryset.page(page_index)
            serializer = self.serializer_class(queryset, many=True)
            return JSONResponse(SuccessResponse({'count': count, 'data':serializer.data}))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))


class LoginLogView(viewsets.ModelViewSet):

    queryset = loginlog.objects.filter(is_deleted=False)
    serializer_class = APILogSerializer
    def list(self, request, *args, **kwargs):
        try:
            page_size = request.GET.get('page_size')
            page_index = request.GET.get('page_index')
            if not page_size:
                page_size = 10
            if not page_index:
                page_index = 1
            queryset = self.filter_queryset(self.get_queryset())
            count = queryset.count()
            try:
                queryset = Paginator(queryset, page_size)
            except EmptyPage:
                    raise InvestError(code=1001)
            queryset = queryset.page(page_index)
            serializer = self.serializer_class(queryset, many=True)
            return JSONResponse(SuccessResponse({'count': count, 'data':serializer.data}))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

class ViewprojLogView(viewsets.ModelViewSet):

    queryset = userviewprojlog.objects.filter(is_deleted=False)
    serializer_class = APILogSerializer
    def list(self, request, *args, **kwargs):
        try:
            page_size = request.GET.get('page_size')
            page_index = request.GET.get('page_index')
            if not page_size:
                page_size = 10
            if not page_index:
                page_index = 1
            queryset = self.filter_queryset(self.get_queryset())
            count = queryset.count()
            try:
                queryset = Paginator(queryset, page_size)
            except EmptyPage:
                    raise InvestError(code=1001)
            queryset = queryset.page(page_index)
            serializer = self.serializer_class(queryset, many=True)
            return JSONResponse(SuccessResponse({'count': count, 'data':serializer.data}))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))