#coding=utf-8
import traceback

import datetime
from django.core.paginator import Paginator, EmptyPage
from django.db import transaction
from django.shortcuts import render

# Create your views here.
from rest_framework import filters
from rest_framework import viewsets

from msg.models import message
from msg.serializer import MsgSerializer
from utils.customClass import InvestError, JSONResponse
from utils.util import logexcption, loginTokenIsAvailable, SuccessResponse, InvestErrorResponse, ExceptionResponse, \
    catchexcption


def saveMessage(content,type,title,receiver,sender=None):
    try:
        data = {}
        data['content'] = content
        data['messagetitle'] = title
        data['type'] = type.id
        data['receiver'] = receiver.id
        data['datasource'] = receiver.datasource_id
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
            page_size = request.GET.get('page_size')
            page_index = request.GET.get('page_index')  # 从第一页开始
            if not page_size:
                page_size = 10
            if not page_index:
                page_index = 1
            queryset = self.filter_queryset(self.get_queryset()).filter(receiver=request.user.id)
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

# class TimeLineRemarkView(viewsets.ModelViewSet):
#     """
#         list:时间轴备注列表
#         create:新建时间轴备注
#         retrieve:查看某一时间轴信息
#         update:修改时间轴信息
#         destroy:删除时间轴
#         """
#     filter_backends = (filters.DjangoFilterBackend,)
#     queryset = timelineremark.objects.all().filter(is_deleted=False)
#     filter_fields = ('timeline',)
#     serializer_class = TimeLineStatuSerializer
#
#
#     def get_queryset(self):
#         assert self.queryset is not None, (
#             "'%s' should either include a `queryset` attribute, "
#             "or override the `get_queryset()` method."
#             % self.__class__.__name__
#         )
#         queryset = self.queryset
#         if isinstance(queryset, QuerySet):
#             if self.request.user.is_authenticated:
#                 queryset = queryset.filter(datasource=self.request.user.datasource)
#             else:
#                 queryset = queryset.all()
#         else:
#             raise InvestError(code=8890)
#         return queryset
#
#     def get_object(self):
#         lookup_url_kwarg = 'pk'
#         try:
#             obj = self.get_queryset().get(id=self.kwargs[lookup_url_kwarg])
#         except timelineremark.DoesNotExist:
#             raise InvestError(code=60021, msg='remark with this "%s" is not exist' % self.kwargs[lookup_url_kwarg])
#         if obj.datasource != self.request.user.datasource:
#             raise InvestError(code=8888,msg='资源非同源')
#         return obj
#
#     @loginTokenIsAvailable()
#     def list(self, request, *args, **kwargs):
#         try:
#             page_size = request.GET.get('page_size')
#             page_index = request.GET.get('page_index')  # 从第一页开始
#             lang = request.GET.get('lang')
#             if not page_size:
#                 page_size = 10
#             if not page_index:
#                 page_index = 1
#             queryset = self.filter_queryset(self.get_queryset())
#             sort = request.GET.get('sort')
#             if sort not in ['True', 'true', True, 1, 'Yes', 'yes', 'YES', 'TRUE']:
#                 queryset = queryset.order_by('-lastmodifytime', '-createdtime')
#             else:
#                 queryset = queryset.order_by('lastmodifytime', 'createdtime')
#             if request.user.has_perm('timeline.admin_getlineremark'):
#                 queryset = queryset
#             else:
#                 queryset = queryset.filter(createuser_id=request.user.id)
#             try:
#                 count = queryset.count()
#                 queryset = Paginator(queryset, page_size)
#                 queryset = queryset.page(page_index)
#             except EmptyPage:
#                 return JSONResponse(SuccessResponse({'count': 0, 'data': []}))
#             serializer = TimeLineRemarkSerializer(queryset, many=True)
#             return JSONResponse(SuccessResponse({'count':count,'data':returnListChangeToLanguage(serializer.data, lang)}))
#         except InvestError as err:
#             return JSONResponse(InvestErrorResponse(err))
#         except Exception:
#             return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))
#
#     def get_timeline(self,id):
#         if self.request.user.is_anonymous:
#             raise InvestError(code=8889)
#         try:
#             line = timeline.objects.get(id=id,is_deleted=False,datasource=self.request.user.datasource)
#         except timeline.DoesNotExist:
#             raise InvestError(code=5002)
#         else:
#             return line
#
#     @loginTokenIsAvailable()
#     def create(self, request, *args, **kwargs):
#         data = request.data
#         lang = request.GET.get('lang')
#         timelineid = data.get('timeline', None)
#         if timelineid:
#             line = self.get_timeline(timelineid)
#             if request.user.has_perm('timeline.admin_addlineremark'):
#                 pass
#             elif request.user.has_perm('timeline.user_getline', line):
#                 pass
#             else:
#                 raise InvestError(code=2009)
#         else:
#             raise InvestError(code=20072)
#         data['createuser'] = request.user.id
#         # if data.get('createuser',None) is None:
#         #     data['createuser'] = request.user.id
#         # createdtime = data.pop('createdtime',None)
#         # if createdtime not in ['None', None, u'None', 'none']:
#         #     data['createdtime'] = datetime.datetime.strptime(createdtime.encode('utf-8')[0:19], "%Y-%m-%d %H:%M:%S")
#         # lastmodifytime = data.pop('lastmodifytime', None)
#         # if lastmodifytime not in ['None', None, u'None', 'none']:
#         #     data['lastmodifytime'] = datetime.datetime.strptime(lastmodifytime.encode('utf-8')[0:19], "%Y-%m-%d %H:%M:%S")
#         data['datasource'] = request.user.datasource.id
#         try:
#             with transaction.atomic():
#                 timeLineremarkserializer = TimeLineRemarkSerializer(data=data)
#                 if timeLineremarkserializer.is_valid():
#                     timeLineremark = timeLineremarkserializer.save()
#                 else:
#                     raise InvestError(code=20071,
#                                       msg='data有误_%s\n%s' % (
#                                           timeLineremarkserializer.error_messages, timeLineremarkserializer.errors))
#                 if timeLineremark.createuser:
#                     add_perm('timeline.user_getlineremark', timeLineremark.createuser, timeLineremark)
#                     add_perm('timeline.user_changelineremark', timeLineremark.createuser, timeLineremark)
#                     add_perm('timeline.user_deletelineremark', timeLineremark.createuser, timeLineremark)
#                 return JSONResponse(SuccessResponse(returnDictChangeToLanguage(timeLineremarkserializer.data, lang)))
#         except InvestError as err:
#             return JSONResponse(InvestErrorResponse(err))
#         except Exception:
#             catchexcption(request)
#             return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))
#
#     @loginTokenIsAvailable()
#     def retrieve(self, request, *args, **kwargs):
#         try:
#             lang = request.GET.get('lang')
#             remark = self.get_object()
#             if request.user.has_perm('timeline.admin_getlineremark'):
#                 timeLineremarkserializer = TimeLineRemarkSerializer
#             elif request.user.has_perm('timeline.user_getlineremark', remark):
#                 timeLineremarkserializer = TimeLineRemarkSerializer
#             else:
#                 raise InvestError(code=2009)
#             serializer = timeLineremarkserializer(remark)
#             return JSONResponse(SuccessResponse(returnDictChangeToLanguage(serializer.data, lang)))
#         except InvestError as err:
#             return JSONResponse(InvestErrorResponse(err))
#         except Exception:
#             catchexcption(request)
#             return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))
#
#     @loginTokenIsAvailable()
#     def update(self, request, *args, **kwargs):
#         try:
#             remark = self.get_object()
#             lang = request.GET.get('lang')
#             if request.user.has_perm('timeline.admin_changelineremark'):
#                 pass
#             elif request.user.has_perm('timeline.user_changelineremark', remark):
#                 pass
#             else:
#                 raise InvestError(code=2009)
#             data = request.data
#             data['lastmodifyuser'] = request.user.id
#             data['lastmodifytime'] = datetime.datetime.now()
#             with transaction.atomic():
#                 serializer = TimeLineRemarkSerializer(remark, data=data)
#                 if serializer.is_valid():
#                     newremark = serializer.save()
#                 else:
#                     raise InvestError(code=20071,
#                                       msg='data有误_%s\n%s' % (serializer.error_messages, serializer.errors))
#                 return JSONResponse(SuccessResponse(returnDictChangeToLanguage(TimeLineRemarkSerializer(newremark).data, lang)))
#         except InvestError as err:
#             return JSONResponse(InvestErrorResponse(err))
#         except Exception:
#             catchexcption(request)
#             return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))
#
#     @loginTokenIsAvailable()
#     def destroy(self, request, *args, **kwargs):
#         try:
#             lang = request.GET.get('lang')
#             instance = self.get_object()
#
#             if request.user.has_perm('timeline.admin_deletelineremark'):
#                 pass
#             elif request.user.has_perm('timeline.user_deletelineremark', instance):
#                 pass
#             else:
#                 raise InvestError(code=2009, msg='没有权限')
#             with transaction.atomic():
#                 instance.is_deleted = True
#                 instance.deleteduser = request.user
#                 instance.deletedtime = datetime.datetime.now()
#                 instance.save()
#                 return JSONResponse(SuccessResponse(returnDictChangeToLanguage(TimeLineRemarkSerializer(instance).data, lang)))
#         except InvestError as err:
#             return JSONResponse(InvestErrorResponse(err))
#         except Exception:
#             catchexcption(request)
#             return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))