#coding=utf-8
import traceback
import datetime
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q, FieldDoesNotExist
# Create your views here.
from django.db.models.fields.reverse_related import ForeignObjectRel
from guardian.shortcuts import assign_perm
from rest_framework import filters , viewsets
from usersys.models import InvestError
from org.models import organization, orgTransactionPhase
from org.serializer import OrgSerializer, OrgCommonSerializer, CreateOrgSerializer, OrgDetailSerializer
from utils import perimissionfields
from utils.util import loginTokenIsAvailable, JSONResponse, catchexcption
from django.db import transaction,models

class OrganizationView(viewsets.ModelViewSet):
    filter_backends = (filters.DjangoFilterBackend,)
    queryset = organization.objects.filter(is_deleted=False)
    filter_fields = ('id','name','orgcode','orgstatu',)
    serializer_class = OrgSerializer

    @loginTokenIsAvailable(['org.admin_getorg','org.user_getorg'])
    def list(self, request, *args, **kwargs):
        page_size = request.GET.get('page_size')
        page_index = request.GET.get('page_index')  # 从第一页开始
        if not page_size:
            page_size = 10
        if not page_index:
            page_index = 1
        queryset = self.filter_queryset(self.queryset)
        try:
            queryset = Paginator(queryset, page_size)
        except EmptyPage:
            return JSONResponse({'success': True, 'result': [], 'errorcode': 1000, 'errormsg': None})
        queryset = queryset.page(page_index)
        serializer = OrgCommonSerializer(queryset, many=True)
        return JSONResponse({'success': True, 'result': serializer.data, 'errorcode': 1000, 'errormsg': None})

    @loginTokenIsAvailable(['org.admin_addorg','org.user_addorg'])
    def create(self, request, *args, **kwargs):
        data = request.data
        data['createuser'] = request.user.id
        data['createtime'] = datetime.datetime.now()
        data['auditStatu'] = 1
        try:
            with transaction.atomic():
                orgTransactionPhases = data.pop('transactionPhases', None)
                orgserializer = CreateOrgSerializer(data=data)
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
                    {'success': True, 'result': OrgSerializer(org).data, 'errorcode': 1000, 'errormsg': None})
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
            if request.user.has_perm('org.admin_getorg'):
                orgserializer = OrgDetailSerializer
            elif request.user.has_perm('org.user_getorg'):
                orgserializer = OrgCommonSerializer
            elif request.user.has_perm('org.user_getorg', org):
                orgserializer = OrgCommonSerializer
            else:
                raise InvestError(code=2009)
            serializer = orgserializer(org)
            return JSONResponse({'success':True,'result': serializer.data,'errorcode':1000,'errormsg':None})
        except InvestError as err:
            return JSONResponse({'success': False, 'result': None, 'errorcode': err.code, 'errormsg': err.msg})
        except Exception:
            catchexcption(request)
            return JSONResponse({'success': False, 'result': None, 'errorcode': 9999,'errormsg': traceback.format_exc().split('\n')[-2]})


    @loginTokenIsAvailable()
    def update(self, request, *args, **kwargs):
        data = request.data
        data['lastmodifyuser'] = request.user.id
        data['lastmodifytime'] = datetime.datetime.now()
        try:
            org = self.get_object()
            if request.user.has_perm('org.admin_changeorg'):
                pass
            elif request.user.has_perm('org.user_getorg', org):
                pass
            else:
                raise InvestError(code=2009)
            with transaction.atomic():
                orgTransactionPhases = data.pop('transactionPhases', None)
                orgserializer = CreateOrgSerializer(org, data=data)
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
                    {'success': True, 'result': OrgSerializer(org).data, 'errorcode': 1000, 'errormsg': None})
        except InvestError as err:
            return JSONResponse({'success': False, 'result': None, 'errorcode': err.code, 'errormsg': err.msg})
        except Exception:
            catchexcption(request)
            return JSONResponse({'success': False, 'result': None, 'errorcode': 9999,
                                 'errormsg': traceback.format_exc().split('\n')[-2]})

    @loginTokenIsAvailable()
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
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
                    if hasattr(manager, 'is_deleted') and manager.is_active:
                        raise InvestError(code=2010, msg=u'{} 上有关联数据'.format(link))
                else:
                    try:
                        manager.model._meta.get_field('is_deleted')
                        if manager.filter(is_active=True).count():
                            raise InvestError(code=2010, msg=u'{} 上有关联数据'.format(link))
                    except FieldDoesNotExist as ex:
                        if manager.count():
                            raise InvestError(code=2010, msg=u'{} 上有关联数据'.format(link))
            with transaction.atomic():
                instance.is_deleted = True
                instance.deleteduser = request.user
                instance.deletedtime = datetime.datetime.utcnow()
                instance.save()
                response = {'success': True, 'result': OrgDetailSerializer(instance).data, 'errorcode': 1000,
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
    queryset = organization.objects.filter(is_deleted=False)
    filter_fields = ('id','name','orgcode','orgstatu',)
    serializer_class = OrgSerializer