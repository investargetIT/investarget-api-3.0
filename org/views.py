#coding=utf-8
import traceback
import datetime
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q, FieldDoesNotExist
# Create your views here.
from django.db.models import QuerySet
from django.db.models.fields.reverse_related import ForeignObjectRel
from guardian.shortcuts import assign_perm
from rest_framework import filters , viewsets
from org.models import organization, orgTransactionPhase, orgRemarks
from org.serializer import OrgSerializer, OrgCommonSerializer, OrgDetailSerializer, \
    OrgRemarkSerializer, OrgRemarkDetailSerializer
from sourcetype.models import TransactionPhases
from utils.myClass import InvestError, JSONResponse
from utils.util import loginTokenIsAvailable, catchexcption, read_from_cache, write_to_cache, returnListChangeToLanguage, \
    returnDictChangeToLanguage
from django.db import transaction,models

class OrganizationView(viewsets.ModelViewSet):
    filter_backends = (filters.DjangoFilterBackend,)
    queryset = organization.objects.filter(is_deleted=False)
    filter_fields = ('id','nameC','orgcode','auditStatu',)
    serializer_class = OrgDetailSerializer
    redis_key = 'organization'

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
            queryset = queryset.all().filter(datasource=self.request.user.datasource)
        else:
            raise InvestError(code=8890)
        return queryset

    def get_object(self, pk=None):
        if pk:
            obj = read_from_cache(self.redis_key + '_%s' % pk)
            if not obj:
                try:
                    obj = self.queryset.get(id=pk)
                except organization.DoesNotExist:
                    raise InvestError(code=5002)
                else:
                    write_to_cache(self.redis_key + '_%s' % pk, obj)
        else:
            lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
            assert lookup_url_kwarg in self.kwargs, (
                'Expected view %s to be called with a URL keyword argument '
                'named "%s". Fix your URL conf, or set the `.lookup_field` '
                'attribute on the view correctly.' %
                (self.__class__.__name__, lookup_url_kwarg)
            )
            obj = read_from_cache(self.redis_key + '_%s' % self.kwargs[lookup_url_kwarg])
            if not obj:
                try:
                    obj = self.queryset.get(id=self.kwargs[lookup_url_kwarg])
                except organization.DoesNotExist:
                    raise InvestError(code=5002)
                else:
                    write_to_cache(self.redis_key + '_%s' % self.kwargs[lookup_url_kwarg], obj)
        if obj.datasource != self.request.user.datasource:
            raise InvestError(code=8888, msg='资源非同源')
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
        if request.user.has_perm('org.admin_getorg'):
            serializerclass = OrgDetailSerializer
        else:
            serializerclass = OrgCommonSerializer
        serializer = serializerclass(queryset, many=True)
        return JSONResponse({'success': True, 'result': returnListChangeToLanguage(serializer.data,lang), 'errorcode': 1000, 'errormsg': None})

    @loginTokenIsAvailable(['org.admin_addorg','org.user_addorg'])
    def create(self, request, *args, **kwargs):
        data = request.data
        lang = request.GET.get('lang')
        data['createuser'] = request.user.id
        data['auditStatu'] = 1
        data['datasource'] = request.user.datasource.id
        try:
            with transaction.atomic():
                orgTransactionPhases = data.pop('transactionPhases', None)
                orgserializer = OrgDetailSerializer(data=data)
                if orgserializer.is_valid():
                    org = orgserializer.save()
                    if orgTransactionPhases:
                        orgTransactionPhaselist = []
                        for transactionPhase in orgTransactionPhases:
                            orgTransactionPhaselist.append(orgTransactionPhase(org=org, transactionPhase_id=transactionPhase,))
                        org.org_orgTransactionPhases.bulk_create(orgTransactionPhaselist)
                else:
                    raise InvestError(code=20071,
                                      msg='data有误_%s\n%s' % (orgserializer.error_messages, orgserializer.errors))
                if org.createuser:
                    assign_perm('org.user_getorg', org.createuser, org)
                    assign_perm('org.user_changeorg', org.createuser, org)
                    assign_perm('org.user_deleteorg', org.createuser, org)
                return JSONResponse(
                    {'success': True, 'result': returnDictChangeToLanguage(OrgSerializer(org).data,lang), 'errorcode': 1000, 'errormsg': None})
        except InvestError as err:
            return JSONResponse({'success': False, 'result': None, 'errorcode': err.code, 'errormsg': err.msg})
        except Exception:
            catchexcption(request)
            return JSONResponse({'success': False, 'result': None, 'errorcode': 9999,
                                 'errormsg': traceback.format_exc().split('\n')[-2]})
    @loginTokenIsAvailable()
    def retrieve(self, request, *args, **kwargs):
        try:
            org = self.get_object()
            lang = request.GET.get('lang')
            if request.user.has_perm('org.admin_getorg'):
                orgserializer = OrgDetailSerializer
            else:
                orgserializer = OrgCommonSerializer
            serializer = orgserializer(org)
            return JSONResponse({'success':True,'result': returnDictChangeToLanguage(serializer.data,lang),'errorcode':1000,'errormsg':None})
        except InvestError as err:
            return JSONResponse({'success': False, 'result': None, 'errorcode': err.code, 'errormsg': err.msg})
        except Exception:
            catchexcption(request)
            return JSONResponse({'success': False, 'result': None, 'errorcode': 9999,'errormsg': traceback.format_exc().split('\n')[-2]})


    @loginTokenIsAvailable()
    def update(self, request, *args, **kwargs):
        data = request.data
        lang = request.GET.get('lang')
        data['lastmodifyuser'] = request.user.id
        data['lastmodifytime'] = datetime.datetime.now()
        try:
            org = self.get_object()
            if request.user.has_perm('org.admin_changeorg'):
                pass
            elif request.user.has_perm('org.user_changeorg', org):
                pass
            else:
                raise InvestError(code=2009)
            with transaction.atomic():
                orgTransactionPhases = data.pop('transactionPhases', None)
                orgserializer = OrgDetailSerializer(org, data=data)
                if orgserializer.is_valid():
                    org = orgserializer.save()
                    if orgTransactionPhases:
                        transactionPhaselist = TransactionPhases.objects.filter(is_deleted=False).in_bulk(orgTransactionPhases)
                        addlist = [item for item in transactionPhaselist if item not in org.orgtransactionphase.all()]
                        removelist = [item for item in org.orgtransactionphase.all() if item not in transactionPhaselist]
                        org.org_orgTransactionPhases.filter(transactionPhase__in=removelist, is_deleted=False).update(is_deleted=True,
                                                                                           deletedtime=datetime.datetime.now(),
                                                                                           deleteduser=request.user)
                        usertaglist = []
                        for transactionPhase in addlist:
                            usertaglist.append(orgTransactionPhase(org=org, transactionPhase=transactionPhase, createuser=request.user))
                        org.org_orgTransactionPhases.bulk_create(usertaglist)
                else:
                    raise InvestError(code=20071,
                                      msg='data有误_%s\n%s' % (orgserializer.error_messages, orgserializer.errors))
                return JSONResponse(
                    {'success': True, 'result': returnDictChangeToLanguage(OrgSerializer(org).data,lang), 'errorcode': 1000, 'errormsg': None})
        except InvestError as err:
            return JSONResponse({'success': False, 'result': None, 'errorcode': err.code, 'errormsg': err.msg})
        except Exception:
            catchexcption(request)
            return JSONResponse({'success': False, 'result': None, 'errorcode': 9999,
                                 'errormsg': traceback.format_exc().split('\n')[-2]})

    @loginTokenIsAvailable(['org.admin_deleteorg',])
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            lang = request.GET.get('lang')
            if request.user.has_perm('org.admin_deleteorg'):
                pass
            elif request.user.has_perm('org.user_deleteorg',instance):
                pass
            else:
                raise InvestError(code=2009)
            rel_fileds = [f for f in instance._meta.get_fields() if isinstance(f, ForeignObjectRel)]
            links = [f.get_accessor_name() for f in rel_fileds]
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
            with transaction.atomic():
                instance.is_deleted = True
                instance.deleteduser = request.user
                instance.deletetime = datetime.datetime.utcnow()
                instance.save()
                response = {'success': True, 'result': returnDictChangeToLanguage(OrgDetailSerializer(instance).data,lang), 'errorcode': 1000,
                            'errormsg': None}
                return JSONResponse(response)
        except InvestError as err:
            return JSONResponse({'success': False, 'result': None, 'errorcode': err.code, 'errormsg': err.msg})
        except Exception:
            catchexcption(request)
            return JSONResponse({'success': False, 'result': None, 'errorcode': 9999,
                                 'errormsg': traceback.format_exc().split('\n')[-2]})

class OrgRemarkView(viewsets.ModelViewSet):
    filter_backends = (filters.DjangoFilterBackend,)
    queryset = orgRemarks.objects.filter(is_deleted=False)
    filter_fields = ('id','org','createuser')
    serializer_class = OrgRemarkSerializer
    redis_key = 'orgemark'
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
            queryset = queryset.all().filter(datasource=self.request.user.datasource)
        else:
            raise InvestError(code=8890)
        return queryset

    def get_object(self, pk=None):
        if pk:
            obj = read_from_cache(self.redis_key + '_%s' % pk)
            if not obj:
                try:
                    obj = self.queryset.get(id=pk)
                except organization.DoesNotExist:
                    raise InvestError(code=5002)
                else:
                    write_to_cache(self.redis_key + '_%s' % pk, obj)
        else:
            lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
            assert lookup_url_kwarg in self.kwargs, (
                'Expected view %s to be called with a URL keyword argument '
                'named "%s". Fix your URL conf, or set the `.lookup_field` '
                'attribute on the view correctly.' %
                (self.__class__.__name__, lookup_url_kwarg)
            )
            obj = read_from_cache(self.redis_key + '_%s' % self.kwargs[lookup_url_kwarg])
            if not obj:
                try:
                    obj = self.queryset.get(id=self.kwargs[lookup_url_kwarg])
                except organization.DoesNotExist:
                    raise InvestError(code=5002)
                else:
                    write_to_cache(self.redis_key + '_%s' % self.kwargs[lookup_url_kwarg], obj)
        if obj.datasource != self.request.user.datasource:
            raise InvestError(code=8888, msg='资源非同源')
        return obj

    @loginTokenIsAvailable(['org.admin_getremark','org.user_getremark'])
    def list(self, request, *args, **kwargs):
        page_size = request.GET.get('page_size')
        page_index = request.GET.get('page_index')  # 从第一页开始
        lang = request.GET.get('lang')
        if not page_size:
            page_size = 10
        if not page_index:
            page_index = 1
        queryset = self.filter_queryset(self.get_queryset())
        if request.user.has_perm('org.admin_getremark'):
            queryset = queryset
        else:
            queryset = queryset.filter(createuser_id=request.user.id)
        try:
            queryset = Paginator(queryset, page_size)
        except EmptyPage:
            return JSONResponse({'success': True, 'result': [], 'errorcode': 1000, 'errormsg': None})
        queryset = queryset.page(page_index)
        serializer = OrgRemarkSerializer(queryset, many=True)
        return JSONResponse({'success': True, 'result': returnListChangeToLanguage(serializer.data,lang), 'errorcode': 1000, 'errormsg': None})

    @loginTokenIsAvailable()
    def create(self, request, *args, **kwargs):
        data = request.data
        lang = request.GET.get('lang')
        data['createuser'] = request.user.id
        data['datasource'] = request.user.datasource.id
        try:
            with transaction.atomic():
                orgremarkserializer = OrgRemarkDetailSerializer(data=data)
                if orgremarkserializer.is_valid():
                    orgremark = orgremarkserializer.save()
                else:
                    raise InvestError(code=20071,
                                      msg='data有误_%s\n%s' % (orgremarkserializer.error_messages, orgremarkserializer.errors))
                if orgremark.createuser:
                    assign_perm('org.user_getremark', orgremark.createuser, orgremark)
                    assign_perm('org.user_changeremark', orgremark.createuser, orgremark)
                    assign_perm('org.user_deleteremark', orgremark.createuser, orgremark)
                return JSONResponse(
                    {'success': True, 'result': returnDictChangeToLanguage(OrgSerializer(orgremark).data,lang), 'errorcode': 1000, 'errormsg': None})
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
            orgremark = self.get_object()
            if request.user.has_perm('org.admin_getremark'):
                orgremarkserializer = OrgRemarkDetailSerializer
            elif request.user.has_perm('org.user_getremark',orgremark):
                orgremarkserializer = OrgRemarkDetailSerializer
            else:
                raise InvestError(code=2009)
            serializer = orgremarkserializer(orgremark)
            return JSONResponse({'success':True,'result': returnDictChangeToLanguage(serializer.data,lang),'errorcode':1000,'errormsg':None})
        except InvestError as err:
            return JSONResponse({'success': False, 'result': None, 'errorcode': err.code, 'errormsg': err.msg})
        except Exception:
            catchexcption(request)
            return JSONResponse({'success': False, 'result': None, 'errorcode': 9999,'errormsg': traceback.format_exc().split('\n')[-2]})

    @loginTokenIsAvailable()
    def update(self, request, *args, **kwargs):
        try:
            org = self.get_object()
            lang = request.GET.get('lang')
            if request.user.has_perm('org.admin_changeremark'):
                pass
            elif request.user.has_perm('org.user_changeremark', org):
                pass
            else:
                raise InvestError(code=2009)
            data = request.data
            data['lastmodifyuser'] = request.user.id
            data['lastmodifytime'] = datetime.datetime.now()
            with transaction.atomic():
                orgTransactionPhases = data.pop('transactionPhases', None)
                orgserializer = OrgRemarkDetailSerializer(org, data=data)
                if orgserializer.is_valid():
                    org = orgserializer.save()
                    if orgTransactionPhases:
                        orgTransactionPhaselist = []
                        for transactionPhase in orgTransactionPhases:
                            orgTransactionPhaselist.append(
                                orgTransactionPhase(org=org, transactionPhase_id=transactionPhase, ))
                        org.org_orgTransactionPhases.bulk_create(orgTransactionPhaselist)
                else:
                    raise InvestError(code=20071,
                                      msg='data有误_%s\n%s' % (orgserializer.error_messages, orgserializer.errors))
                return JSONResponse(
                    {'success': True, 'result': returnDictChangeToLanguage(OrgSerializer(org).data,lang), 'errorcode': 1000, 'errormsg': None})
        except InvestError as err:
            return JSONResponse({'success': False, 'result': None, 'errorcode': err.code, 'errormsg': err.msg})
        except Exception:
            catchexcption(request)
            return JSONResponse({'success': False, 'result': None, 'errorcode': 9999,
                                 'errormsg': traceback.format_exc().split('\n')[-2]})

    @loginTokenIsAvailable()
    def destroy(self, request, *args, **kwargs):
        try:
            lang = request.GET.get('lang')
            instance = self.get_object()

            if request.user.has_perm('org.admin_deleteremark'):
                pass
            elif request.user.has_perm('org.user_deleteremark', instance):
                pass
            else:
                raise InvestError(code=2009, msg='没有权限')
            with transaction.atomic():
                instance.is_deleted = True
                instance.deleteduser = request.user
                instance.deletedtime = datetime.datetime.now()
                instance.save()
                response = {'success': True, 'result': returnDictChangeToLanguage(OrgRemarkDetailSerializer(instance).data,lang),'errorcode':1000,'errormsg':None}
                return JSONResponse(response)
        except InvestError as err:
            return JSONResponse({'success': False, 'result': None, 'errorcode': err.code, 'errormsg': err.msg})
        except Exception:
            catchexcption(request)
            return JSONResponse({'success': False, 'result': None, 'errorcode': 9999,
                                 'errormsg': traceback.format_exc().split('\n')[-2]})