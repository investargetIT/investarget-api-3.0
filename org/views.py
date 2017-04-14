#coding=utf-8
import traceback
import datetime
from django.core.paginator import Paginator, EmptyPage
from django.db import transaction
from django.db.models import Q
# Create your views here.
from rest_framework import filters , viewsets
from usersys.models import InvestError
from org.models import organization, orgTransactionPhase
from org.serializer import OrgSerializer, OrgCommonSerializer, CreateOrgSerializer
from utils import perimissionfields
from utils.util import loginTokenIsAvailable, JSONResponse, catchexcption


class OrganizationView(viewsets.ModelViewSet):
    filter_backends = (filters.DjangoFilterBackend,)
    queryset = organization.objects.filter(is_deleted=False)
    filter_fields = ('id','name','orgcode','orgstatu',)
    serializer_class = OrgSerializer

    @loginTokenIsAvailable(['usersys.as_adminuser'])
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

    @loginTokenIsAvailable(['org.adminadd_org','org.add_organization'])
    def create(self, request, *args, **kwargs):
        data = request.data
        data['createuser'] = request.user.id
        data['createtime'] = datetime.datetime.now()
        try:
            with transaction.atomic():
                orgTransactionPhases = data.pop('transactionPhases', None)
                orgserializer = CreateOrgSerializer(data=data)
                if orgserializer.is_valid():
                    org = orgserializer.save()
                    if orgTransactionPhases:
                        usertaglist = []
                        for transactionPhase in orgTransactionPhases:
                            usertaglist.append(orgTransactionPhase(org=org, transactionPhase_id=transactionPhase,))
                        org.org_orgTransactionPhases.bulk_create(usertaglist)
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


    def update(self, request, *args, **kwargs):
        pass


class OrgRemarkView(viewsets.ModelViewSet):
    filter_backends = (filters.DjangoFilterBackend,)
    queryset = organization.objects.filter(is_deleted=False)
    filter_fields = ('id','name','orgcode','orgstatu',)
    serializer_class = OrgSerializer