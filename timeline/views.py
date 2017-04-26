#coding=utf-8
import traceback

from django.core.paginator import Paginator, EmptyPage
from django.db import models
from django.db import transaction
from django.db.models import Q,QuerySet, FieldDoesNotExist
from rest_framework import filters, viewsets

from timeline.models import timeline, timelineTransationStatu, timelineremark
from timeline.serializer import TimeLineSerializer, TimeLineStatuSerializer, TimeLineCreateSerializer, \
    TimeLineHeaderListSerializer, TimeLineStatuCreateSerializer
from utils.myClass import InvestError, JSONResponse
from utils.util import read_from_cache, write_to_cache, returnListChangeToLanguage, loginTokenIsAvailable, \
    returnDictChangeToLanguage, catchexcption, cache_delete_key
import datetime

class TimelineView(viewsets.ModelViewSet):
    filter_backends = (filters.DjangoFilterBackend,)
    queryset = timeline.objects.all().filter(is_deleted=False)
    filter_fields = ('proj', 'investor','trader','supporter','isClose')
    serializer_class = TimeLineSerializer
    redis_key = 'timeline'
    Model = timeline

    def get_queryset(self):
        if self.request.user.is_anonymous:
            raise InvestError(code=8889)
        assert self.queryset is not None, (
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method."
            % self.__class__.__name__
        )
        queryset = self.queryset
        if isinstance(queryset, QuerySet):
            queryset = queryset.filter(datasource=self.request.user.datasource)
        else:
            raise InvestError(code=8890)
        return queryset

    def get_object(self,pk=None):
        if pk:
            obj = read_from_cache(self.redis_key + '_%s' % pk)
            if not obj:
                try:
                    obj = self.Model.objects.get(id=pk, is_deleted=False)
                except self.Model.DoesNotExist:
                    raise InvestError(code=6002, msg='timeline with this "%s" is not exist' % pk)
                else:
                    write_to_cache(self.redis_key + '_%s' % pk, obj)
        else:
            lookup_url_kwarg = 'pk'
            obj = read_from_cache(self.redis_key + '_%s' % self.kwargs[lookup_url_kwarg])
            if not obj:
                try:
                    obj = self.Model.objects.get(id=self.kwargs[lookup_url_kwarg], is_deleted=False)
                except self.Model.DoesNotExist:
                    raise InvestError(code=6002,msg='timeline with this "%s" is not exist' % self.kwargs[lookup_url_kwarg])
                else:
                    write_to_cache(self.redis_key + '_%s' % self.kwargs[lookup_url_kwarg], obj)
        if obj.datasource != self.request.user.datasource:
            raise InvestError(code=8888,msg='资源非同源')
        return obj

    @loginTokenIsAvailable()
    def list(self, request, *args, **kwargs):
        page_size = request.GET.get('page_size')
        page_index = request.GET.get('page_index')  # 从第一页开始
        lang = request.GET.get('lang')
        if not page_size:
            page_size = 10
        if not page_index:
            page_index = 1
        queryset = self.filter_queryset(self.get_queryset())
        try:
            queryset = Paginator(queryset, page_size)
        except EmptyPage:
            return JSONResponse({'success': True, 'result': [], 'errorcode': 1000, 'errormsg': None})
        queryset = queryset.page(page_index)
        serializer = TimeLineHeaderListSerializer(queryset, many=True)
        return JSONResponse(
            {'success': True, 'result': returnListChangeToLanguage(serializer.data, lang), 'errorcode': 1000,
             'errormsg': None})

    @loginTokenIsAvailable(['timeline.admin_addline','timeline.user_addline'])
    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            lang = request.GET.get('lang')
            data['createuser'] = request.user.id
            data['datasource'] = request.user.datasource.id
            with transaction.atomic():
                timelineserializer = TimeLineCreateSerializer(data=data)
                if timelineserializer.is_valid():
                    timeline = timelineserializer.save()
                    data['timeline'] = timeline.id
                    timelinestatu = TimeLineStatuCreateSerializer(data=data)
                    if timelinestatu.is_valid():
                        timelinestatu.save()
                    else:
                        raise InvestError(code=20071,msg=timelinestatu.errors)
                else:
                    raise InvestError(code=20071,msg=timelineserializer.errors)
                return JSONResponse(
                    {'success': True, 'result': returnDictChangeToLanguage(TimeLineSerializer(timeline).data, lang),
                     'errorcode': 1000, 'errormsg': None})
        except InvestError as err:
            return JSONResponse({'success': False, 'result': None, 'errorcode': err.code, 'errormsg': err.msg})
        except Exception:
            catchexcption(request)
            return JSONResponse({'success': False, 'result': None, 'errorcode': 9999,
                                 'errormsg': traceback.format_exc().split('\n')[-2]})

    @loginTokenIsAvailable()
    def retrieve(self, request, *args, **kwargs):
        try:
            lang = request.GET.get('lang')
            instance = self.get_object()
            if request.user.has_perm('timeline.admin_getline'):
                serializerclass = TimeLineSerializer
            elif request.user == instance.investor or request.user == instance.trader or request.user == instance.supporter:
                serializerclass = TimeLineSerializer
            else:
                raise InvestError(code=2009)
            serializer = serializerclass(instance)
            return JSONResponse(
                {'success': True, 'result': returnDictChangeToLanguage(serializer.data, lang), 'errorcode': 1000,
                 'errormsg': None})
        except InvestError as err:
            return JSONResponse({'success': False, 'result': None, 'errorcode': err.code, 'errormsg': err.msg})
        except Exception:
            catchexcption(request)
            return JSONResponse({'success': False, 'result': None, 'errorcode': 9999,
                                 'errormsg': traceback.format_exc().split('\n')[-2]})

    @loginTokenIsAvailable()
    def update(self, request, *args, **kwargs):
        try:
            timeline = self.get_object()
            data = request.data
            lang = request.GET.get('lang')
            timelinedata = data.pop('timelinedata',None)
            statudata = data.pop('statudata',None)
            if statudata:
                timelinetransationStatus = statudata.get('transationStatus')
                if timelinetransationStatus:
                    statudata['lastmodifyuser'] = request.user.id
                    statudata['lastmodifytime'] = datetime.datetime.now()
                    statudata['timeline'] = timeline.id
                    statudata['isActive'] = True
                    timelinestatus = timeline.timeline_transationStatus.all().filter(transationStatus__id=timelinetransationStatus,is_deleted=False)
                    if timelinestatus.exists():
                        if timelinestatus.count() > 1:
                            raise InvestError(code=6001)
                        else:
                            activetimelinestatu = timelinestatus.first()
                    else:
                        activetimelinestatu = None
                    with transaction.atomic():
                        timeline.timeline_transationStatus.all().update(isActive=False)
                        timelinestatu = TimeLineStatuCreateSerializer(activetimelinestatu,data=statudata)
                        if timelinestatu.is_valid():
                            timelinestatu.save()
                        else:
                            raise InvestError(code=20071, msg=timelinestatu.errors)
            if timelinedata:
                timelinedata['lastmodifyuser'] = request.user.id
                timelinedata['lastmodifytime'] = datetime.datetime.now()
                with transaction.atomic():
                    timelineseria = TimeLineCreateSerializer(timeline,data=timelinedata)
                    if timelineseria.is_valid():
                        timelineseria.save()
                    else:
                        raise InvestError(code=20071, msg=timelineseria.errors)
            return JSONResponse(
                    {'success': True, 'result': returnDictChangeToLanguage(TimeLineSerializer(timeline).data, lang),
                     'errorcode': 1000, 'errormsg': None})
        except InvestError as err:
            return JSONResponse({'success': False, 'result': None, 'errorcode': err.code, 'errormsg': err.msg})
        except Exception:
            catchexcption(request)
            return JSONResponse({'success': False, 'result': None, 'errorcode': 9999,
                                 'errormsg': traceback.format_exc().split('\n')[-2]})

    # delete
    @loginTokenIsAvailable(['timeline.admin_deleteline'])
    def destroy(self, request, *args, **kwargs):
        try:
            timelineidlist = request.data
            timelinelist = []
            lang = request.GET.get('lang')
            if not timelineidlist:
                raise InvestError(code=20071, msg='except a not null list')
            with transaction.atomic():
                for timelineid in timelineidlist:
                    instance = self.get_object(timelineid)
                    links = []
                    for link in links:
                        manager = getattr(instance, link, None)
                        if not manager:
                            continue
                        # one to one
                        if isinstance(manager, models.Model):
                            if hasattr(manager, 'is_deleted') and not manager.is_deleted:
                                raise InvestError(code=2010, msg=u'{} 上有关联数据'.format(link))
                        else:
                            try:
                                manager.model._meta.get_field('is_deleted')
                                if manager.all().filter(is_deleted=False).count():
                                    raise InvestError(code=2010, msg=u'{} 上有关联数据'.format(link))
                            except FieldDoesNotExist as ex:
                                if manager.all().count():
                                    raise InvestError(code=2010, msg=u'{} 上有关联数据'.format(link))
                    instance.is_deleted = True
                    instance.deleteduser = request.user
                    instance.deletedtime = datetime.datetime.now()
                    instance.save()
                    instance.timeline_transationStatus.all().update(is_deleted=True)
                    instance.timeline_remarks.all().update(is_deleted=True)
                    cache_delete_key(self.redis_key + '_%s' % instance.id)
                    timelinelist.append(TimeLineSerializer(instance).data)
                response = {'success': True, 'result': returnListChangeToLanguage(timelinelist, lang),
                            'errorcode': 1000, 'errormsg': None}
                return JSONResponse(response)
        except InvestError as err:
            return JSONResponse({'success': False, 'result': None, 'errorcode': err.code, 'errormsg': err.msg})
        except Exception:
            catchexcption(request)
            return JSONResponse({'success': False, 'result': None, 'errorcode': 9999,
                                 'errormsg': traceback.format_exc().split('\n')[-2]})





class TimeLineRemarkView(viewsets.ModelViewSet):
    filter_backends = (filters.DjangoFilterBackend,)
    queryset = timelineremark.objects.all().filter(is_deleted=False)
    filter_fields = ('timeline',)
    serializer_class = TimeLineStatuSerializer


    def get_queryset(self):
        if self.request.user.is_anonymous:
            raise InvestError(code=8889)
        assert self.queryset is not None, (
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method."
            % self.__class__.__name__
        )
        queryset = self.queryset
        if isinstance(queryset, QuerySet):
            queryset = queryset.filter(datasource=self.request.user.datasource)
        else:
            raise InvestError(code=8890)
        return queryset

    def get_object(self):
        lookup_url_kwarg = 'pk'
        try:
            obj = self.get_queryset().get(id=self.kwargs[lookup_url_kwarg])
        except timelineremark.DoesNotExist:
            raise InvestError(code=60021, msg='remark with this "%s" is not exist' % self.kwargs[lookup_url_kwarg])
        return obj

    @loginTokenIsAvailable()
    def list(self, request, *args, **kwargs):
        page_size = request.GET.get('page_size')
        page_index = request.GET.get('page_index')  # 从第一页开始
        lang = request.GET.get('lang')
        if not page_size:
            page_size = 10
        if not page_index:
            page_index = 1
        queryset = self.filter_queryset(self.get_queryset())
        try:
            queryset = Paginator(queryset, page_size)
        except EmptyPage:
            return JSONResponse({'success': True, 'result': [], 'errorcode': 1000, 'errormsg': None})
        queryset = queryset.page(page_index)
        serializer = TimeLineHeaderListSerializer(queryset, many=True)
        return JSONResponse(
            {'success': True, 'result': returnListChangeToLanguage(serializer.data, lang), 'errorcode': 1000,
             'errormsg': None})