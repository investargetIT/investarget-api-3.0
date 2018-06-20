#coding=utf-8
import traceback
import datetime
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q, FieldDoesNotExist, Max
# Create your views here.
from django.db.models import QuerySet
from rest_framework import filters , viewsets

from org.models import organization, orgTransactionPhase, orgRemarks, orgContact, orgBuyout, orgManageFund, orgInvestEvent, orgCooperativeRelationship, \
    orgTags
from org.serializer import OrgCommonSerializer, OrgDetailSerializer, OrgRemarkDetailSerializer, OrgCreateSerializer,\
    OrgUpdateSerializer, OrgBuyoutCreateSerializer, OrgContactCreateSerializer, OrgInvestEventCreateSerializer,\
    OrgManageFundCreateSerializer, OrgCooperativeRelationshipCreateSerializer, OrgBuyoutSerializer, OrgContactSerializer, \
    OrgInvestEventSerializer, OrgManageFundSerializer, OrgCooperativeRelationshipSerializer
from sourcetype.models import TransactionPhases, TagContrastTable
from utils.customClass import InvestError, JSONResponse, RelationFilter, MySearchFilter
from utils.util import loginTokenIsAvailable, catchexcption, read_from_cache, write_to_cache, returnListChangeToLanguage, \
    returnDictChangeToLanguage, SuccessResponse, InvestErrorResponse, ExceptionResponse, setrequestuser, add_perm, \
    cache_delete_key, mySortQuery
from django.db import transaction,models
from django_filters import FilterSet


class OrganizationFilter(FilterSet):
    orgfullname = RelationFilter(filterstr='orgfullname')
    ids = RelationFilter(filterstr='id', lookup_method='in')
    lv = RelationFilter(filterstr='orglevel', lookup_method='in')
    stockcode = RelationFilter(filterstr='stockcode',lookup_method='in')
    stockshortname = RelationFilter(filterstr='stockshortname',lookup_method='in')
    issub = RelationFilter(filterstr='issub', lookup_method='exact')
    investoverseasproject = RelationFilter(filterstr='investoverseasproject', lookup_method='exact')
    industrys = RelationFilter(filterstr='industry',lookup_method='in')
    currencys = RelationFilter(filterstr='currency',lookup_method='in')
    orgname = RelationFilter(filterstr='orgnameC')
    orgtransactionphases = RelationFilter(filterstr='orgtransactionphase',lookup_method='in',relationName='org_orgTransactionPhases__is_deleted')
    orgtypes = RelationFilter(filterstr='orgtype',lookup_method='in')
    orgstatus = RelationFilter(filterstr='orgstatus',lookup_method='in')
    area = RelationFilter(filterstr='org_users__orgarea',lookup_method='in',relationName='org_users__is_deleted')
    trader = RelationFilter(filterstr='org_users__investor_relations__traderuser',lookup_method='in',relationName='org_users__investor_relations__is_deleted')
    class Meta:
        model = organization
        fields = ['orgname','orgstatus','currencys','industrys','orgtransactionphases','orgtypes','area','trader','stockcode','stockshortname','issub','investoverseasproject', 'ids', 'lv']

class OrganizationView(viewsets.ModelViewSet):
    """
    list:获取机构列表
    create:新增机构
    retrieve:查看机构详情
    update:修改机构信息
    destroy:删除机构
    """
    filter_backends = (MySearchFilter,filters.DjangoFilterBackend,)
    queryset = organization.objects.filter(is_deleted=False)
    filter_class = OrganizationFilter
    search_fields = ('orgnameC','orgnameE','stockcode', 'orgfullname')
    serializer_class = OrgDetailSerializer
    redis_key = 'organization'

    def get_object(self, pk=None):
        if pk:
            obj = read_from_cache(self.redis_key + '_%s' % pk)
            if not obj:
                try:
                    obj = self.get_queryset().get(id=pk)
                except organization.DoesNotExist:
                    raise InvestError(code=5002)
                else:
                    write_to_cache(self.redis_key + '_%s' % pk, obj)
        else:
            lookup_url_kwarg = 'pk'
            obj = read_from_cache(self.redis_key + '_%s' % self.kwargs[lookup_url_kwarg])
            if not obj:
                try:
                    obj = self.get_queryset().get(id=self.kwargs[lookup_url_kwarg])
                except organization.DoesNotExist:
                    raise InvestError(code=5002)
                else:
                    write_to_cache(self.redis_key + '_%s' % self.kwargs[lookup_url_kwarg], obj)
        return obj


    def list(self, request, *args, **kwargs):
        try:
            page_size = request.GET.get('page_size', 10)
            page_index = request.GET.get('page_index', 1)
            lang = request.GET.get('lang', 'cn')
            queryset = self.filter_queryset(self.get_queryset())
            tags = request.GET.get('tags', None)
            if tags:
                tags = tags.split(',')
                queryset = queryset.filter(Q(org_users__tags__in=tags) | Q(org_orgtags__tag__in=tags))
            sortfield = request.GET.get('sort', 'createdtime')
            desc = request.GET.get('desc', 1)
            queryset = mySortQuery(queryset, sortfield, desc)
            setrequestuser(request)
            if request.user.is_anonymous:
                serializerclass = OrgCommonSerializer
            else:
                if request.user.has_perm('org.admin_getorg'):
                    serializerclass = OrgDetailSerializer
                else:
                    serializerclass = OrgCommonSerializer  # warning
            try:
                count = queryset.count()
                queryset = Paginator(queryset, page_size)
                queryset = queryset.page(page_index)
            except EmptyPage:
                return JSONResponse(SuccessResponse({'count': 0, 'data': []}))
            responselist = []
            for instance in queryset:
                actionlist = {'get': False, 'change': False, 'delete': False}
                user_count = 0
                if request.user.is_anonymous:
                    pass
                else:
                    if instance.orglevel_id == 1:
                        user_count = self.checkOrgUserContactInfoTruth(instance, request.user.datasource)
                    if request.user.has_perm('org.admin_getorg') or request.user.has_perm('org.user_getorg',instance):
                        actionlist['get'] = True
                    if request.user.has_perm('org.admin_changeorg') or request.user.has_perm('org.user_changeorg',instance):
                        actionlist['change'] = True
                    if request.user.has_perm('org.admin_deleteorg') or request.user.has_perm('org.user_deleteorg',instance):
                        actionlist['delete'] = True
                instancedata = serializerclass(instance).data
                instancedata['action'] = actionlist
                instancedata['user_count'] = user_count
                responselist.append(instancedata)
            return JSONResponse(SuccessResponse({'count':count,'data':returnListChangeToLanguage(responselist,lang)}))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))


    def checkOrgUserContactInfoTruth(self, org, datasource):
        user_qs = org.org_users.all().filter(is_deleted=False, datasource=datasource)
        count = user_qs.filter(Q(mobile__regex=r'^[1](3[0-9]|47|5[0-9]|8[0-9])[0-9]{8}$')).count()
        print count
        return count


    @loginTokenIsAvailable()
    def create(self, request, *args, **kwargs):
        data = request.data
        lang = request.GET.get('lang')
        data['createuser'] = request.user.id
        data['datasource'] = request.user.datasource.id
        if request.user.has_perm('org.admin_addorg'):
            pass
        elif request.user.has_perm('org.user_addorg'):
            data['orgstatus'] = 1
        else:
            raise InvestError(2009)
        try:
            with transaction.atomic():
                orgTransactionPhases = data.pop('orgtransactionphase', None)
                orgserializer = OrgCreateSerializer(data=data)
                if orgserializer.is_valid():
                    org = orgserializer.save()
                    if orgTransactionPhases and isinstance(orgTransactionPhases,list):
                        orgTransactionPhaselist = []
                        for transactionPhase in orgTransactionPhases:
                            orgTransactionPhaselist.append(orgTransactionPhase(org=org, transactionPhase_id=transactionPhase,createuser=request.user,createdtime=datetime.datetime.now()))
                        org.org_orgTransactionPhases.bulk_create(orgTransactionPhaselist)
                    tags = data.pop('tags', None)
                    if tags:
                        orgtaglist = []
                        for tag in tags:
                            orgtaglist.append(orgTags(org=org, tag_id=tag, createdtime=datetime.datetime.now()))
                        org.org_orgtags.bulk_create(orgtaglist)
                else:
                    raise InvestError(code=20071, msg='data有误_%s' % orgserializer.errors)
                if org.createuser:
                    add_perm('org.user_getorg', org.createuser, org)
                    add_perm('org.user_changeorg', org.createuser, org)
                    add_perm('org.user_deleteorg', org.createuser, org)
                return JSONResponse(SuccessResponse(returnDictChangeToLanguage(OrgDetailSerializer(org).data,lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable()
    def retrieve(self, request, *args, **kwargs):
        try:
            org = self.get_object()
            orgusers = org.org_users.all().filter(is_deleted=False)
            lang = request.GET.get('lang')
            if request.user.has_perm('org.admin_getorg'):
                orgserializer = OrgDetailSerializer
            elif request.user.has_perm('org.user_getorg', org):
                orgserializer = OrgDetailSerializer
            elif request.user.org == org:
                orgserializer = OrgDetailSerializer
            elif request.user.trader_relations.all().filter(is_deleted=False, investoruser__in=orgusers).exists():
                orgserializer = OrgDetailSerializer
            else:
                orgserializer = OrgCommonSerializer
            serializer = orgserializer(org)
            return JSONResponse(SuccessResponse(returnDictChangeToLanguage(serializer.data,lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))


    @loginTokenIsAvailable()
    def update(self, request, *args, **kwargs):
        data = request.data
        lang = request.GET.get('lang')
        IPOdate = data.pop('IPOdate', None)
        if IPOdate not in ['None', None, u'None', 'none']:
            data['IPOdate'] = datetime.datetime.strptime(IPOdate[0:10], '%Y-%m-%d')
        data['lastmodifyuser'] = request.user.id
        data['lastmodifytime'] = datetime.datetime.now()
        try:
            org = self.get_object()
            if request.user.has_perm('org.admin_changeorg'):
                pass
            elif request.user.has_perm('org.user_changeorg', org):
                data.pop('orgstatus', None)
            else:
                raise InvestError(code=2009)
            with transaction.atomic():
                orgTransactionPhases = data.pop('orgtransactionphase', None)
                tags = data.pop('tags', None)
                orgupdateserializer = OrgUpdateSerializer(org, data=data)
                if orgupdateserializer.is_valid():
                    org = orgupdateserializer.save()
                    if orgTransactionPhases:
                        transactionPhaselist = TransactionPhases.objects.filter(is_deleted=False).in_bulk(orgTransactionPhases)
                        addlist = [item for item in transactionPhaselist if item not in org.orgtransactionphase.all()]
                        removelist = [item for item in org.orgtransactionphase.all() if item not in transactionPhaselist]
                        org.org_orgTransactionPhases.filter(transactionPhase__in=removelist, is_deleted=False).delete()
                        usertaglist = []
                        for transactionPhase in addlist:
                            usertaglist.append(orgTransactionPhase(org=org, transactionPhase_id=transactionPhase, createuser=request.user,createdtime=datetime.datetime.now()))
                        org.org_orgTransactionPhases.bulk_create(usertaglist)
                    if tags:
                        org.org_orgtags.all().delete()
                        orgtaglist = []
                        for tag in tags:
                            orgtaglist.append(orgTags(org=org, tag_id=tag, createdtime=datetime.datetime.now()))
                        org.org_orgtags.bulk_create(orgtaglist)
                else:
                    raise InvestError(code=20071,
                                      msg='data有误_%s\n%s' % (orgupdateserializer.error_messages, orgupdateserializer.errors))
                cache_delete_key(self.redis_key + '_%s' % org.id)
                return JSONResponse(SuccessResponse(returnDictChangeToLanguage(OrgDetailSerializer(org).data,lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable()
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            lang = request.GET.get('lang')
            if request.user.has_perm('org.admin_deleteorg'):
                pass
            elif request.user.has_perm('org.user_deleteorg',instance) and instance.orgstatus != 2:
                pass
            else:
                raise InvestError(code=2009)
            with transaction.atomic():
                for link in ['org_users','org_orgTransactionPhases','org_remarks','org_unreachuser','org_orgBDs','org_orgInvestEvent'
                             'org_orgManageFund','fund_fundManager','org_orgcontact','org_cooperativeRelationship','cooperativeorg_Relationship'
                             'org_buyout','buyoutorg_buyoutorg']:
                    if link in ['org_users', 'org_orgBDs']:
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
                            except FieldDoesNotExist:
                                if manager.all().count():
                                    raise InvestError(code=2010, msg=u'{} 上有关联数据，且没有is_deleted字段'.format(link))
                    else:
                        manager = getattr(instance, link, None)
                        if not manager:
                            continue
                        # one to one
                        if isinstance(manager, models.Model):
                            if hasattr(manager, 'is_deleted') and not manager.is_deleted:
                                manager.is_deleted = True
                                manager.save()
                        else:
                            try:
                                manager.model._meta.get_field('is_deleted')
                                if manager.all().filter(is_deleted=False).count():
                                    manager.all().update(is_deleted=True)
                            except FieldDoesNotExist:
                                pass
                instance.is_deleted = True
                instance.deleteduser = request.user
                instance.deletetime = datetime.datetime.utcnow()
                instance.save()
                cache_delete_key(self.redis_key + '_%s' % instance.id)
                return JSONResponse(SuccessResponse(returnDictChangeToLanguage(OrgDetailSerializer(instance).data,lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

class OrgRemarkView(viewsets.ModelViewSet):
    """
    list:获取机构备注列表
    create:新增机构备注
    retrieve:查看机构某条备注详情（id）
    update:修改机构备注信息（id）
    destroy:删除机构备注 （id）
    """
    filter_backends = (filters.DjangoFilterBackend,)
    queryset = orgRemarks.objects.filter(is_deleted=False)
    filter_fields = ('id','org','createuser')
    serializer_class = OrgRemarkDetailSerializer


    def get_object(self, pk=None):
        if pk:
            try:
                obj = self.queryset.get(id=pk)
            except orgRemarks.DoesNotExist:
                raise InvestError(code=5002)
        else:
            try:
                obj = self.queryset.get(id=self.kwargs['pk'])
            except orgRemarks.DoesNotExist:
                raise InvestError(code=5002)
        if obj.datasource != self.request.user.datasource:
            raise InvestError(code=8888)
        return obj

    def get_org(self,orgid):
        if self.request.user.is_anonymous:
            raise InvestError(code=8889)
        try:
            org = organization.objects.get(id=orgid,is_deleted=False)
        except organization.DoesNotExist:
            raise InvestError(code=5002)
        else:
            return org

    @loginTokenIsAvailable()
    def list(self, request, *args, **kwargs):
        try:
            page_size = request.GET.get('page_size', 10)
            page_index = request.GET.get('page_index', 1)
            lang = request.GET.get('lang', 'cn')
            queryset = self.filter_queryset(self.get_queryset())
            if request.user.has_perm('org.admin_getorgremark'):
                queryset = queryset.filter(datasource=request.user.datasource)
            else:
                queryset = queryset.filter(createuser_id=request.user.id)
            try:
                count = queryset.count()
                queryset = Paginator(queryset, page_size)
                queryset = queryset.page(page_index)
            except EmptyPage:
                return JSONResponse(SuccessResponse({'count': 0, 'data': []}))
            serializer = OrgRemarkDetailSerializer(queryset, many=True)
            return JSONResponse(SuccessResponse({'count':count,'data':returnListChangeToLanguage(serializer.data,lang)}))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable()
    def create(self, request, *args, **kwargs):
        data = request.data
        lang = request.GET.get('lang')
        orgid = data.get('org',None)
        if orgid:
            org = self.get_org(orgid=orgid)
            if request.user.has_perm('org.admin_addorgremark'):
                pass
            elif request.user.has_perm('org.user_addorgremark'):
                pass
            else:
                raise InvestError(code=2009)
        else:
            raise InvestError(code=20072)
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
                    add_perm('org.user_getorgremark', orgremark.createuser, orgremark)
                    add_perm('org.user_changeorgremark', orgremark.createuser, orgremark)
                    add_perm('org.user_deleteorgremark', orgremark.createuser, orgremark)
                return JSONResponse(SuccessResponse(returnDictChangeToLanguage(OrgRemarkDetailSerializer(orgremark).data,lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable()
    def retrieve(self, request, *args, **kwargs):
        try:
            lang = request.GET.get('lang')
            orgremark = self.get_object()
            if request.user.has_perm('org.admin_getorgremark'):
                orgremarkserializer = OrgRemarkDetailSerializer
            elif request.user.has_perm('org.user_getorgremark',orgremark):
                orgremarkserializer = OrgRemarkDetailSerializer
            else:
                raise InvestError(code=2009)
            serializer = orgremarkserializer(orgremark)
            return JSONResponse(SuccessResponse(returnDictChangeToLanguage(serializer.data,lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable()
    def update(self, request, *args, **kwargs):
        try:
            orgremark = self.get_object()
            lang = request.GET.get('lang')
            if request.user.has_perm('org.admin_changeorgremark'):
                pass
            elif request.user.has_perm('org.user_changeorgremark', orgremark):
                pass
            else:
                raise InvestError(code=2009)
            data = request.data
            data['lastmodifyuser'] = request.user.id
            data['lastmodifytime'] = datetime.datetime.now()
            data.pop('datasource', None)
            with transaction.atomic():
                orgserializer = OrgRemarkDetailSerializer(orgremark, data=data)
                if orgserializer.is_valid():
                    org = orgserializer.save()
                else:
                    raise InvestError(code=20071,
                                      msg='data有误_%s' % orgserializer.errors)
                return JSONResponse(SuccessResponse(returnDictChangeToLanguage(OrgRemarkDetailSerializer(org).data,lang)))
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

            if request.user.has_perm('org.admin_deleteorgremark'):
                pass
            elif request.user.has_perm('org.user_deleteorgremark', instance):
                pass
            else:
                raise InvestError(code=2009, msg='没有权限')
            with transaction.atomic():
                instance.is_deleted = True
                instance.deleteduser = request.user
                instance.deletedtime = datetime.datetime.now()
                instance.save()
                return JSONResponse(SuccessResponse(returnDictChangeToLanguage(OrgRemarkDetailSerializer(instance).data,lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))


class OrgContactView(viewsets.ModelViewSet):
    """
    list:获取机构联系方式
    create:新增机构联系方式
    retrieve:查看机构某条联系方式详情（id）
    update:修改机构联系方式（id）
    destroy:删除机构联系方式（id）
    """
    filter_backends = (filters.DjangoFilterBackend,)
    queryset = orgContact.objects.filter(is_deleted=False).filter(org__is_deleted=False)
    filter_fields = ('id','org','createuser')
    serializer_class = OrgContactSerializer
    models = orgContact

    def get_object(self, pk=None):
        if pk:
            try:
                obj = self.queryset.get(id=pk)
            except self.models.DoesNotExist:
                raise InvestError(code=5002)
        else:
            try:
                obj = self.queryset.get(id=self.kwargs['pk'])
            except self.models.DoesNotExist:
                raise InvestError(code=5002)
        return obj

    def get_org(self,orgid):
        if self.request.user.is_anonymous:
            raise InvestError(code=8889)
        try:
            org = organization.objects.get(id=orgid,is_deleted=False)
        except organization.DoesNotExist:
            raise InvestError(code=5002)
        else:
            return org

    @loginTokenIsAvailable()
    def list(self, request, *args, **kwargs):
        try:
            page_size = request.GET.get('page_size', 10)
            page_index = request.GET.get('page_index', 1)
            lang = request.GET.get('lang', 'cn')
            orgid = request.GET.get('org', None)
            if not orgid:
                raise InvestError(2007, msg='机构不能为空')
            else:
                orginstace = self.get_org(orgid)
            queryset = self.filter_queryset(self.get_queryset())
            try:
                count = queryset.count()
                queryset = Paginator(queryset, page_size)
                queryset = queryset.page(page_index)
            except EmptyPage:
                return JSONResponse(SuccessResponse({'count': 0, 'data': []}))
            serializer = self.serializer_class(queryset, many=True)
            return JSONResponse(SuccessResponse({'count':count,'data':returnListChangeToLanguage(serializer.data,lang)}))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable()
    def create(self, request, *args, **kwargs):
        data = request.data
        lang = request.GET.get('lang')
        orgid = data.get('org',None)
        if orgid:
            org = self.get_org(orgid=orgid)
            if request.user.has_perm('org.admin_changeorg'):
                pass
            elif request.user.has_perm('org.user_changeorg', org):
                pass
            else:
                raise InvestError(code=2009)
        else:
            raise InvestError(code=20072)
        data['createuser'] = request.user.id
        try:
            with transaction.atomic():
                instanceserializer = OrgContactCreateSerializer(data=data)
                if instanceserializer.is_valid():
                    instance = instanceserializer.save()
                else:
                    raise InvestError(code=20071,msg='data有误_%s' % instanceserializer.error_messages)
                return JSONResponse(SuccessResponse(returnDictChangeToLanguage(self.serializer_class(instance).data,lang)))
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
            serializer = self.serializer_class(instance)
            return JSONResponse(SuccessResponse(returnDictChangeToLanguage(serializer.data,lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable()
    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            lang = request.GET.get('lang')
            if request.user.has_perm('org.admin_changeorg'):
                pass
            elif request.user.has_perm('org.user_changeorg', instance):
                pass
            else:
                raise InvestError(code=2009)
            data = request.data
            data['lastmodifytime'] = datetime.datetime.now()
            with transaction.atomic():
                instanceserializer = OrgContactCreateSerializer(instance, data=data)
                if instanceserializer.is_valid():
                    newinstance = instanceserializer.save()
                else:
                    raise InvestError(code=20071,  msg='data有误_%s' % instanceserializer.errors)
                return JSONResponse(SuccessResponse(returnDictChangeToLanguage(self.serializer_class(newinstance).data,lang)))
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
            if request.user.has_perm('org.admin_changeorg'):
                pass
            elif request.user.has_perm('org.user_changeorg', instance):
                pass
            else:
                raise InvestError(code=2009, msg='没有权限')
            with transaction.atomic():
                instance.is_deleted = True
                instance.deleteduser = request.user
                instance.deletedtime = datetime.datetime.now()
                instance.save()
                return JSONResponse(SuccessResponse(returnDictChangeToLanguage(self.serializer_class(instance).data,lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))


class OrgManageFundView(viewsets.ModelViewSet):
    """
    list:获取机构管理基金
    create:新增机构管理基金
    retrieve:查看机构某条管理基金详情（id）
    update:修改机构管理基金（id）
    destroy:删除机构管理基金id）
    """
    filter_backends = (filters.DjangoFilterBackend,)
    queryset = orgManageFund.objects.filter(is_deleted=False).filter(org__is_deleted=False, fund__is_deleted=False)
    filter_fields = ('id','org','createuser')
    serializer_class = OrgManageFundSerializer
    models = orgManageFund

    def get_object(self, pk=None):
        if pk:
            try:
                obj = self.queryset.get(id=pk)
            except self.models.DoesNotExist:
                raise InvestError(code=5002)
        else:
            try:
                obj = self.queryset.get(id=self.kwargs['pk'])
            except self.models.DoesNotExist:
                raise InvestError(code=5002)
        return obj

    def get_org(self,orgid):
        if self.request.user.is_anonymous:
            raise InvestError(code=8889)
        try:
            org = organization.objects.get(id=orgid,is_deleted=False)
        except organization.DoesNotExist:
            raise InvestError(code=5002)
        else:
            return org

    @loginTokenIsAvailable()
    def list(self, request, *args, **kwargs):
        try:
            page_size = request.GET.get('page_size', 10)
            page_index = request.GET.get('page_index', 1)
            lang = request.GET.get('lang', 'cn')
            orgid = request.GET.get('org', None)
            if not orgid:
                raise InvestError(2007, msg='机构不能为空')
            else:
                orginstace = self.get_org(orgid)
            queryset = self.filter_queryset(self.get_queryset())
            try:
                count = queryset.count()
                queryset = Paginator(queryset, page_size)
                queryset = queryset.page(page_index)
            except EmptyPage:
                return JSONResponse(SuccessResponse({'count': 0, 'data': []}))
            serializer = self.serializer_class(queryset, many=True)
            return JSONResponse(SuccessResponse({'count':count,'data':returnListChangeToLanguage(serializer.data,lang)}))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable()
    def create(self, request, *args, **kwargs):
        data = request.data
        lang = request.GET.get('lang')
        orgid = data.get('org',None)
        if orgid:
            org = self.get_org(orgid=orgid)
            if request.user.has_perm('org.admin_changeorg'):
                pass
            elif request.user.has_perm('org.user_changeorg', org):
                pass
            else:
                raise InvestError(code=2009)
        else:
            raise InvestError(code=20072)
        data['createuser'] = request.user.id
        try:
            with transaction.atomic():
                instanceserializer = OrgManageFundCreateSerializer(data=data)
                if instanceserializer.is_valid():
                    instance = instanceserializer.save()
                else:
                    raise InvestError(code=20071,msg='data有误_%s' % instanceserializer.error_messages)
                return JSONResponse(SuccessResponse(returnDictChangeToLanguage(self.serializer_class(instance).data,lang)))
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
            serializer = self.serializer_class(instance)
            return JSONResponse(SuccessResponse(returnDictChangeToLanguage(serializer.data,lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable()
    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            lang = request.GET.get('lang')
            if request.user.has_perm('org.admin_changeorg'):
                pass
            elif request.user.has_perm('org.user_changeorg', instance):
                pass
            else:
                raise InvestError(code=2009)
            data = request.data
            data['lastmodifytime'] = datetime.datetime.now()
            with transaction.atomic():
                instanceserializer = OrgManageFundCreateSerializer(instance, data=data)
                if instanceserializer.is_valid():
                    newinstance = instanceserializer.save()
                else:
                    raise InvestError(code=20071,  msg='data有误_%s' % instanceserializer.errors)
                return JSONResponse(SuccessResponse(returnDictChangeToLanguage(self.serializer_class(newinstance).data,lang)))
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
            if request.user.has_perm('org.admin_changeorg'):
                pass
            elif request.user.has_perm('org.user_changeorg', instance):
                pass
            else:
                raise InvestError(code=2009, msg='没有权限')
            with transaction.atomic():
                instance.is_deleted = True
                instance.deleteduser = request.user
                instance.deletedtime = datetime.datetime.now()
                instance.save()
                return JSONResponse(SuccessResponse(returnDictChangeToLanguage(self.serializer_class(instance).data,lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))


class OrgInvestEventView(viewsets.ModelViewSet):
    """
    list:获取机构投资事件
    create:新增机构投资事件
    retrieve:查看机构某条投资事件详情（id）
    update:修改机构投资事件（id）
    destroy:删除机构投资事件id）
    """
    filter_backends = (filters.DjangoFilterBackend,)
    queryset = orgInvestEvent.objects.filter(is_deleted=False).filter(org__is_deleted=False)
    filter_fields = ('id','org','createuser')
    serializer_class = OrgInvestEventSerializer
    models = orgInvestEvent

    def get_object(self, pk=None):
        if pk:
            try:
                obj = self.queryset.get(id=pk)
            except self.models.DoesNotExist:
                raise InvestError(code=5002)
        else:
            try:
                obj = self.queryset.get(id=self.kwargs['pk'])
            except self.models.DoesNotExist:
                raise InvestError(code=5002)
        return obj

    def get_org(self,orgid):
        if self.request.user.is_anonymous:
            raise InvestError(code=8889)
        try:
            org = organization.objects.get(id=orgid,is_deleted=False)
        except organization.DoesNotExist:
            raise InvestError(code=5002)
        else:
            return org

    @loginTokenIsAvailable()
    def list(self, request, *args, **kwargs):
        try:
            page_size = request.GET.get('page_size', 10)
            page_index = request.GET.get('page_index', 1)
            lang = request.GET.get('lang', 'cn')
            orgid = request.GET.get('org', None)
            if not orgid:
                raise InvestError(2007, msg='机构不能为空')
            else:
                orginstace = self.get_org(orgid)
            queryset = self.filter_queryset(self.get_queryset()).order_by('-investDate')
            try:
                count = queryset.count()
                queryset = Paginator(queryset, page_size)
                queryset = queryset.page(page_index)
            except EmptyPage:
                return JSONResponse(SuccessResponse({'count': 0, 'data': []}))
            serializer = self.serializer_class(queryset, many=True)
            return JSONResponse(SuccessResponse({'count':count,'data':returnListChangeToLanguage(serializer.data,lang)}))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable()
    def create(self, request, *args, **kwargs):
        data = request.data
        lang = request.GET.get('lang')
        orgid = data.get('org',None)
        if orgid:
            org = self.get_org(orgid=orgid)
            if request.user.has_perm('org.admin_changeorg'):
                pass
            elif request.user.has_perm('org.user_changeorg', org):
                pass
            else:
                raise InvestError(code=2009)
        else:
            raise InvestError(code=20072)
        data['createuser'] = request.user.id
        industrytype = data.get('industrytype', None)
        Pindustrytype = data.get('Pindustrytype', None)
        try:
            with transaction.atomic():
                instanceserializer = OrgInvestEventCreateSerializer(data=data)
                if instanceserializer.is_valid():
                    instance = instanceserializer.save()
                    useP = False
                    if industrytype:
                        for tag_id in TagContrastTable.objects.filter(cat_name=industrytype).values_list('tag_id'):
                            useP = True
                            if not orgTags.objects.filter(org_id=orgid, tag_id=tag_id[0]).exists():
                                orgTags(org_id=orgid, tag_id=tag_id[0]).save()
                    if not useP:
                        if Pindustrytype:
                            for tag_id in TagContrastTable.objects.filter(cat_name=Pindustrytype).values_list('tag_id'):
                                if not orgTags.objects.filter(org_id=orgid, tag_id=tag_id[0]).exists():
                                    orgTags(org_id=orgid, tag_id=tag_id[0]).save()
                else:
                    raise InvestError(code=20071,msg='data有误_%s' % instanceserializer.error_messages)
                return JSONResponse(SuccessResponse(returnDictChangeToLanguage(self.serializer_class(instance).data,lang)))
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
            serializer = self.serializer_class(instance)
            return JSONResponse(SuccessResponse(returnDictChangeToLanguage(serializer.data,lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable()
    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            lang = request.GET.get('lang')
            if request.user.has_perm('org.admin_changeorg'):
                pass
            elif request.user.has_perm('org.user_changeorg', instance):
                pass
            else:
                raise InvestError(code=2009)
            data = request.data
            data['lastmodifytime'] = datetime.datetime.now()
            industrytype = data.get('industrytype', None)
            Pindustrytype = data.get('Pindustrytype', None)
            with transaction.atomic():
                instanceserializer = OrgInvestEventCreateSerializer(instance, data=data)
                if instanceserializer.is_valid():
                    newinstance = instanceserializer.save()
                    useP = False
                    if industrytype:
                        for tag_id in TagContrastTable.objects.filter(cat_name=industrytype).values_list('tag_id'):
                            useP = True
                            if not orgTags.objects.filter(org_id=newinstance.org_id, tag_id=tag_id[0]).exists():
                                orgTags(org_id=newinstance.org_id, tag_id=tag_id[0]).save()
                    if not useP:
                        if Pindustrytype:
                            for tag_id in TagContrastTable.objects.filter(cat_name=Pindustrytype).values_list('tag_id'):
                                if not orgTags.objects.filter(org_id=newinstance.org_id, tag_id=tag_id[0]).exists():
                                    orgTags(org_id=newinstance.org_id, tag_id=tag_id[0]).save()
                else:
                    raise InvestError(code=20071,  msg='data有误_%s' % instanceserializer.errors)
                return JSONResponse(SuccessResponse(returnDictChangeToLanguage(self.serializer_class(newinstance).data,lang)))
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
            if request.user.has_perm('org.admin_changeorg'):
                pass
            elif request.user.has_perm('org.user_changeorg', instance):
                pass
            else:
                raise InvestError(code=2009, msg='没有权限')
            with transaction.atomic():
                instance.is_deleted = True
                instance.deleteduser = request.user
                instance.deletedtime = datetime.datetime.now()
                instance.save()
                return JSONResponse(SuccessResponse(returnDictChangeToLanguage(self.serializer_class(instance).data,lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable()
    def deleteInvest(self, request, *args, **kwargs):
        try:
            if request.user.is_superuser:
                orgid = request.GET.get('org')
                day = request.GET.get('day', 10)
                if isinstance(day, (unicode, str)):
                    day = int(day)
                orginstance = organization.objects.get(id=orgid)
                self.queryset.filter(org=orginstance, is_deleted=False, createdtime__lt=(datetime.datetime.now() - datetime.timedelta(days=day))).update(**{'is_deleted': True,'deletedtime':datetime.datetime.now()})
            return JSONResponse(SuccessResponse({'a':'b'}))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))


class OrgCooperativeRelationshipView(viewsets.ModelViewSet):
    """
    list:获取机构合作关系
    create:新增机构合作关系
    retrieve:查看机构某条合作关系详情（id）
    update:修改机构合作关系（id）
    destroy:删除机构合作关系id）
    """
    filter_backends = (filters.DjangoFilterBackend,)
    queryset = orgCooperativeRelationship.objects.filter(is_deleted=False).filter(org__is_deleted=False, cooperativeOrg__is_deleted=False)
    filter_fields = ('id','createuser',)
    serializer_class = OrgCooperativeRelationshipSerializer
    models = orgCooperativeRelationship

    def get_object(self, pk=None):
        if pk:
            try:
                obj = self.queryset.get(id=pk)
            except self.models.DoesNotExist:
                raise InvestError(code=5002)
        else:
            try:
                obj = self.queryset.get(id=self.kwargs['pk'])
            except self.models.DoesNotExist:
                raise InvestError(code=5002)
        return obj

    def get_org(self,orgid):
        if self.request.user.is_anonymous:
            raise InvestError(code=8889)
        try:
            org = organization.objects.get(id=orgid,is_deleted=False)
        except organization.DoesNotExist:
            raise InvestError(code=5002)
        else:
            return org

    @loginTokenIsAvailable()
    def list(self, request, *args, **kwargs):
        try:
            page_size = request.GET.get('page_size', 10)
            page_index = request.GET.get('page_index', 1)
            lang = request.GET.get('lang', 'cn')
            orgid = request.GET.get('org', None)
            if not orgid:
                raise InvestError(2007, msg='机构不能为空')
            else:
                orginstace = self.get_org(orgid)
            queryset = self.filter_queryset(self.get_queryset()).filter(Q(org=orginstace)).order_by('-investDate')
            # queryset = self.filter_queryset(self.get_queryset()).filter(Q(org=orginstace)|Q(cooperativeOrg=orginstace)).order_by('-investDate')
            try:
                count = queryset.count()
                queryset = Paginator(queryset, page_size)
                queryset = queryset.page(page_index)
            except EmptyPage:
                return JSONResponse(SuccessResponse({'count': 0, 'data': []}))
            serializer = self.serializer_class(queryset, many=True)
            return JSONResponse(SuccessResponse({'count':count,'data':returnListChangeToLanguage(serializer.data,lang)}))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable()
    def create(self, request, *args, **kwargs):
        data = request.data
        lang = request.GET.get('lang')
        orgid = data.get('org',None)
        if orgid:
            org = self.get_org(orgid=orgid)
            if request.user.has_perm('org.admin_changeorg'):
                pass
            elif request.user.has_perm('org.user_changeorg', org):
                pass
            else:
                raise InvestError(code=2009)
        else:
            raise InvestError(code=20072)
        data['createuser'] = request.user.id
        try:
            with transaction.atomic():
                instanceserializer = OrgCooperativeRelationshipCreateSerializer(data=data)
                if instanceserializer.is_valid():
                    instance = instanceserializer.save()
                else:
                    raise InvestError(code=20071,msg='data有误_%s' % instanceserializer.error_messages)
                return JSONResponse(SuccessResponse(returnDictChangeToLanguage(self.serializer_class(instance).data,lang)))
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
            serializer = self.serializer_class(instance)
            return JSONResponse(SuccessResponse(returnDictChangeToLanguage(serializer.data,lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable()
    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            lang = request.GET.get('lang')
            if request.user.has_perm('org.admin_changeorg'):
                pass
            elif request.user.has_perm('org.user_changeorg', instance):
                pass
            else:
                raise InvestError(code=2009)
            data = request.data
            data['lastmodifytime'] = datetime.datetime.now()
            with transaction.atomic():
                instanceserializer = OrgCooperativeRelationshipCreateSerializer(instance, data=data)
                if instanceserializer.is_valid():
                    newinstance = instanceserializer.save()
                else:
                    raise InvestError(code=20071,  msg='data有误_%s' % instanceserializer.errors)
                return JSONResponse(SuccessResponse(returnDictChangeToLanguage(self.serializer_class(newinstance).data,lang)))
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
            if request.user.has_perm('org.admin_changeorg'):
                pass
            elif request.user.has_perm('org.user_changeorg', instance):
                pass
            else:
                raise InvestError(code=2009, msg='没有权限')
            with transaction.atomic():
                instance.is_deleted = True
                instance.deleteduser = request.user
                instance.deletedtime = datetime.datetime.now()
                instance.save()
                return JSONResponse(SuccessResponse(returnDictChangeToLanguage(self.serializer_class(instance).data,lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

class OrgBuyoutView(viewsets.ModelViewSet):
    """
    list:获取机构退出分析
    create:新增机构退出分析
    retrieve:查看机构某条退出分析详情（id）
    update:修改机构退出分析（id）
    destroy:删除机构退出分析（id）
    """
    filter_backends = (filters.DjangoFilterBackend,)
    queryset = orgBuyout.objects.filter(is_deleted=False).filter(org__is_deleted=False, buyoutorg__is_deleted=False)
    filter_fields = ('id','org','createuser')
    serializer_class = OrgBuyoutSerializer
    models = orgBuyout

    def get_object(self, pk=None):
        if pk:
            try:
                obj = self.queryset.get(id=pk)
            except self.models.DoesNotExist:
                raise InvestError(code=5002)
        else:
            try:
                obj = self.queryset.get(id=self.kwargs['pk'])
            except self.models.DoesNotExist:
                raise InvestError(code=5002)
        return obj

    def get_org(self,orgid):
        if self.request.user.is_anonymous:
            raise InvestError(code=8889)
        try:
            org = organization.objects.get(id=orgid,is_deleted=False)
        except organization.DoesNotExist:
            raise InvestError(code=5002)
        else:
            return org

    @loginTokenIsAvailable()
    def list(self, request, *args, **kwargs):
        try:
            page_size = request.GET.get('page_size', 10)
            page_index = request.GET.get('page_index', 1)
            lang = request.GET.get('lang', 'cn')
            orgid = request.GET.get('org', None)
            if not orgid:
                raise InvestError(2007, msg='机构不能为空')
            else:
                orginstace = self.get_org(orgid)
            queryset = self.filter_queryset(self.get_queryset()).order_by('-buyoutDate')
            try:
                count = queryset.count()
                queryset = Paginator(queryset, page_size)
                queryset = queryset.page(page_index)
            except EmptyPage:
                return JSONResponse(SuccessResponse({'count': 0, 'data': []}))
            serializer = self.serializer_class(queryset, many=True)
            return JSONResponse(SuccessResponse({'count':count,'data':returnListChangeToLanguage(serializer.data,lang)}))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable()
    def create(self, request, *args, **kwargs):
        data = request.data
        lang = request.GET.get('lang')
        orgid = data.get('org',None)
        if orgid:
            org = self.get_org(orgid=orgid)
            if request.user.has_perm('org.admin_changeorg'):
                pass
            elif request.user.has_perm('org.user_changeorg', org):
                pass
            else:
                raise InvestError(code=2009)
        else:
            raise InvestError(code=20072)
        data['createuser'] = request.user.id
        try:
            with transaction.atomic():
                instanceserializer = OrgBuyoutCreateSerializer(data=data)
                if instanceserializer.is_valid():
                    instance = instanceserializer.save()
                else:
                    raise InvestError(code=20071,msg='data有误_%s' % instanceserializer.error_messages)
                return JSONResponse(SuccessResponse(returnDictChangeToLanguage(self.serializer_class(instance).data,lang)))
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
            serializer = self.serializer_class(instance)
            return JSONResponse(SuccessResponse(returnDictChangeToLanguage(serializer.data,lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable()
    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            lang = request.GET.get('lang')
            if request.user.has_perm('org.admin_changeorg'):
                pass
            elif request.user.has_perm('org.user_changeorg', instance):
                pass
            else:
                raise InvestError(code=2009)
            data = request.data
            data['lastmodifytime'] = datetime.datetime.now()
            with transaction.atomic():
                instanceserializer = OrgBuyoutCreateSerializer(instance, data=data)
                if instanceserializer.is_valid():
                    newinstance = instanceserializer.save()
                else:
                    raise InvestError(code=20071,  msg='data有误_%s' % instanceserializer.errors)
                return JSONResponse(SuccessResponse(returnDictChangeToLanguage(self.serializer_class(newinstance).data,lang)))
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
            if request.user.has_perm('org.admin_changeorg'):
                pass
            elif request.user.has_perm('org.user_changeorg', instance):
                pass
            else:
                raise InvestError(code=2009, msg='没有权限')
            with transaction.atomic():
                instance.is_deleted = True
                instance.deleteduser = request.user
                instance.deletedtime = datetime.datetime.now()
                instance.save()
                return JSONResponse(SuccessResponse(returnDictChangeToLanguage(self.serializer_class(instance).data,lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))