#coding=utf-8
import traceback

import datetime
from django.core.paginator import Paginator, EmptyPage
from django.db import transaction

# Create your views here.
from rest_framework import filters
from rest_framework import viewsets

from msg.models import message, schedule
from msg.serializer import MsgSerializer, ScheduleSerializer, ScheduleCreateSerializer
from utils.customClass import InvestError, JSONResponse
from utils.util import logexcption, loginTokenIsAvailable, SuccessResponse, InvestErrorResponse, ExceptionResponse, \
    catchexcption, returnListChangeToLanguage, returnDictChangeToLanguage, mySortQuery


def saveMessage(content,type,title,receiver,sender=None,modeltype=None,sourceid=None):
    try:
        data = {}
        data['content'] = content
        data['messagetitle'] = title
        data['type'] = type
        data['receiver'] = receiver.id
        data['datasource'] = receiver.datasource_id
        if modeltype:
            data['sourcetype'] = modeltype
        if sourceid:
            data['sourceid'] = sourceid
        if sender:
            data['sender'] = sender.id
        msg = MsgSerializer(data=data)
        if msg.is_valid():
            msg.save()
        else:
            raise InvestError(code=20019)
        return msg.data
    except InvestError as err:
        logexcption()
        return err.msg
    except Exception as err:
        logexcption()
        return err.message


class WebMessageView(viewsets.ModelViewSet):
    """
    list:获取站内信列表
    update:已读回执
    """
    filter_backends = (filters.DjangoFilterBackend,)
    queryset = message.objects.all().filter(is_deleted=False)
    filter_fields = ('datasource','type','isRead','receiver')
    serializer_class = MsgSerializer


    @loginTokenIsAvailable()
    def list(self, request, *args, **kwargs):
        try:
            page_size = request.GET.get('page_size', 10)
            page_index = request.GET.get('page_index', 1)
            lang = request.GET.get('lang', 'cn')
            queryset = self.filter_queryset(self.get_queryset()).filter(receiver=request.user.id).order_by('-createdtime',)
            try:
                count = queryset.count()
                queryset = Paginator(queryset, page_size)
                queryset = queryset.page(page_index)
            except EmptyPage:
                return JSONResponse(SuccessResponse({'count': 0, 'data': []}))
            serializer = MsgSerializer(queryset, many=True)
            return JSONResponse(SuccessResponse({'count':count,'data':serializer.data}))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable()
    def update(self, request, *args, **kwargs):
        try:
            msg = self.get_object()
            if msg.receiver.id != request.user.id:
                raise InvestError(2009)
            with transaction.atomic():
                data = {
                    'isRead':True,
                    'readtime':datetime.datetime.now(),
                }
                msgserializer = MsgSerializer(msg, data=data)
                if msgserializer.is_valid():
                    msgserializer.save()
                else:
                    raise InvestError(code=20071,msg='data有误_%s' % msgserializer.errors)
                return JSONResponse(SuccessResponse(msgserializer.data))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

class ScheduleView(viewsets.ModelViewSet):
    """
        list:日程安排列表
        create:新建日程
        retrieve:查看某一日程安排信息
        update:修改日程安排信息
        destroy:删除日程安排
        """
    filter_backends = (filters.SearchFilter, filters.DjangoFilterBackend,)
    queryset = schedule.objects.all().filter(is_deleted=False)
    filter_fields = ('proj','createuser','user','projtitle','country')
    search_fields = ('createuser__usernameC', 'user__usernameC', 'user__mobile', 'proj__projtitleC', 'proj__projtitleE')
    serializer_class = ScheduleSerializer


    @loginTokenIsAvailable()
    def list(self, request, *args, **kwargs):
        try:
            page_size = request.GET.get('page_size', 10)
            page_index = request.GET.get('page_index', 1)
            lang = request.GET.get('lang', 'cn')
            date = request.GET.get('date')
            time = request.GET.get('time')
            queryset = self.filter_queryset(self.queryset.filter(datasource=request.user.datasource_id))
            if date:
                date = datetime.datetime.strptime(date.encode('utf-8'), "%Y-%m-%d")
                queryset = queryset.filter(scheduledtime__year=date.year,scheduledtime__month=date.month)
            if time:
                time = datetime.datetime.strptime(time.encode('utf-8'), "%Y-%m-%dT%H:%M:%S")
                queryset = queryset.filter(scheduledtime__gt=time)
            if request.user.has_perm('msg.admin_manageSchedule'):
                queryset = queryset
            else:
                queryset = queryset.filter(createuser_id=request.user.id)
            sortfield = request.GET.get('sort', 'scheduledtime')
            desc = request.GET.get('desc', 0)
            queryset = mySortQuery(queryset, sortfield, desc)
            try:
                count = queryset.count()
                queryset = Paginator(queryset, page_size)
                queryset = queryset.page(page_index)
            except EmptyPage:
                return JSONResponse(SuccessResponse({'count': 0, 'data': []}))
            serializer = ScheduleSerializer(queryset, many=True)
            return JSONResponse(SuccessResponse({'count':count,'data':returnListChangeToLanguage(serializer.data, lang)}))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))


    @loginTokenIsAvailable()
    def create(self, request, *args, **kwargs):
        data = request.data
        lang = request.GET.get('lang')
        data['createuser'] = request.user.id
        data['datasource'] = request.user.datasource.id
        try:
            with transaction.atomic():
                scheduleserializer = ScheduleCreateSerializer(data=data)
                if scheduleserializer.is_valid():
                    scheduleserializer.save()
                else:
                    raise InvestError(code=20071,
                                      msg='data有误_%s\n%s' % (
                                          scheduleserializer.error_messages, scheduleserializer.errors))
                return JSONResponse(SuccessResponse(returnDictChangeToLanguage(scheduleserializer.data, lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable()
    def retrieve(self, request, *args, **kwargs):
        try:
            lang = request.GET.get('lang')
            instance = self.get_object()
            if request.user.has_perm('msg.admin_manageSchedule'):
                pass
            elif request.user == instance.createuser:
                pass
            else:
                raise InvestError(code=2009)
            serializer = ScheduleSerializer(instance)
            return JSONResponse(SuccessResponse(returnDictChangeToLanguage(serializer.data, lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable()
    def update(self, request, *args, **kwargs):
        try:
            lang = request.GET.get('lang')
            instance = self.get_object()
            if request.user.has_perm('msg.admin_manageSchedule'):
                pass
            elif request.user == instance.createuser:
                pass
            else:
                raise InvestError(code=2009)
            data = request.data
            data['lastmodifyuser'] = request.user.id
            data['lastmodifytime'] = datetime.datetime.now()
            with transaction.atomic():
                serializer = ScheduleCreateSerializer(instance, data=data)
                if serializer.is_valid():
                    newinstance = serializer.save()
                else:
                    raise InvestError(code=20071, msg='data有误_%s' %  serializer.errors)
                return JSONResponse(SuccessResponse(returnDictChangeToLanguage(ScheduleSerializer(newinstance).data, lang)))
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
            if request.user.has_perm('msg.admin_manageSchedule'):
                pass
            elif request.user == instance.createuser:
                pass
            else:
                raise InvestError(code=2009)
            with transaction.atomic():
                instance.is_deleted = True
                instance.deleteduser = request.user
                instance.deletedtime = datetime.datetime.now()
                instance.save()
                return JSONResponse(SuccessResponse(returnDictChangeToLanguage(ScheduleCreateSerializer(instance).data, lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))