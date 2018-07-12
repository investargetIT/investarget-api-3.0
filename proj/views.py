#coding=utf-8
import json
import os
import traceback

import pdfkit
from django.core.paginator import Paginator, EmptyPage
from django.db import models,transaction
from django.db.models import Q,QuerySet
from django.core.exceptions import FieldDoesNotExist
from django.http import HttpResponse
from django.http import StreamingHttpResponse
from django.shortcuts import render
from rest_framework import filters, viewsets
import datetime

from rest_framework.decorators import detail_route

from APIlog.views import viewprojlog
from dataroom.views import pulishProjectCreateDataroom
from invest.settings import PROJECTPDF_URLPATH, APILOG_PATH
from proj.models import project, finance, projectTags, projectIndustries, projectTransactionType, favoriteProject, \
    ShareToken, attachment, projServices
from proj.serializer import ProjSerializer, FinanceSerializer, ProjCreatSerializer, \
    ProjCommonSerializer, FinanceChangeSerializer, FinanceCreateSerializer, FavoriteSerializer, \
    FavoriteCreateSerializer, ProjAttachmentSerializer, ProjListSerializer_admin , ProjListSerializer_user, \
    ProjDetailSerializer_admin_withoutsecretinfo, ProjDetailSerializer_admin_withsecretinfo, ProjDetailSerializer_user_withoutsecretinfo, \
    ProjDetailSerializer_user_withsecretinfo, ProjAttachmentCreateSerializer, ProjIndustryCreateSerializer, \
    ProjDetailSerializer_all
from sourcetype.models import Tag, Industry, TransactionType, DataSource, Service
from third.views.jpush import pushnotification
from third.views.qiniufile import deleteqiniufile
from usersys.models import MyUser
from utils.somedef import addWaterMark, file_iterator
from utils.sendMessage import sendmessage_favoriteproject, sendmessage_projectpublish
from utils.util import catchexcption, read_from_cache, write_to_cache, loginTokenIsAvailable, returnListChangeToLanguage, \
    returnDictChangeToLanguage, SuccessResponse, InvestErrorResponse, ExceptionResponse, setrequestuser, \
    setUserObjectPermission, cache_delete_key, checkrequesttoken, rem_perm, logexcption
from utils.customClass import JSONResponse, InvestError, RelationFilter
from django_filters import FilterSet

class ProjectFilter(FilterSet):
    supportUser = RelationFilter(filterstr='supportUser',lookup_method='in')
    ids = RelationFilter(filterstr='id', lookup_method='in')
    createuser = RelationFilter(filterstr='createuser', lookup_method='in')
    ismarketplace = RelationFilter(filterstr='ismarketplace', lookup_method='exact')
    isoverseasproject = RelationFilter(filterstr='isoverseasproject', lookup_method='in')
    industries = RelationFilter(filterstr='industries',lookup_method='in',relationName='project_industries__is_deleted')
    tags = RelationFilter(filterstr='tags',lookup_method='in',relationName='project_tags__is_deleted')
    service = RelationFilter(filterstr='proj_services__service', lookup_method='in', relationName='proj_services__is_deleted')
    projstatus = RelationFilter(filterstr='projstatus',lookup_method='in')
    bdm =  RelationFilter(filterstr='proj_orgBDs__manager', lookup_method='in')
    country = RelationFilter(filterstr='country',lookup_method='in')
    netIncome_USD_F = RelationFilter(filterstr='proj_finances__netIncome_USD',lookup_method='gte')
    netIncome_USD_T = RelationFilter(filterstr='proj_finances__netIncome_USD', lookup_method='lte')
    grossProfit_F = RelationFilter(filterstr='proj_finances__grossProfit', lookup_method='gte')
    grossProfit_T = RelationFilter(filterstr='proj_finances__grossProfit', lookup_method='lte')
    class Meta:
        model = project
        fields = ('ids', 'bdm', 'createuser','service','supportUser','ismarketplace','isoverseasproject','industries','tags','projstatus','country','netIncome_USD_F','netIncome_USD_T','grossProfit_F','grossProfit_T')


class ProjectView(viewsets.ModelViewSet):
    """
    list:获取项目列表
    create:创建项目
    retrieve:获取项目详情
    update:修改项目
    destroy:删除项目
    getshareprojtoken:获取分享项目token
    getshareproj:获取分享的项目详情
    sendWXGroupPdf:发送群pdf
    """
    filter_backends = (filters.SearchFilter,filters.DjangoFilterBackend,)
    queryset = project.objects.all().filter(is_deleted=False)
    filter_class = ProjectFilter
    search_fields = ('projtitleC', 'projtitleE',)
    serializer_class = ProjSerializer
    redis_key = 'project'
    Model = project

    def get_queryset(self):
        assert self.queryset is not None, (
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method."
            % self.__class__.__name__
        )
        queryset = self.queryset
        if isinstance(queryset, QuerySet):
            if self.request.user.is_authenticated:
                queryset = queryset.filter(datasource=self.request.user.datasource)
            else:
                queryset = queryset.all()
        else:
            raise InvestError(code=8890)
        return queryset

    def get_object(self):
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
                obj = self.Model.objects.get(id=self.kwargs[lookup_url_kwarg], is_deleted=False)
            except self.Model.DoesNotExist:
                raise InvestError(code=4002,msg='proj with this "%s" is not exist' % self.kwargs[lookup_url_kwarg])
            else:
                write_to_cache(self.redis_key + '_%s' % self.kwargs[lookup_url_kwarg], obj)
        if obj.datasource != self.request.user.datasource:
            raise InvestError(code=8888)
        return obj

    def list(self, request, *args, **kwargs):
        try:
            max_size = request.GET.get('max_size')
            skip_count = request.GET.get('skip_count')  # 从第一页开始
            lang = request.GET.get('lang')
            source = request.META.get('HTTP_SOURCE')
            if source:
                datasource = DataSource.objects.filter(id=source, is_deleted=False)
                if datasource.exists():
                    userdatasource = datasource.first()
                    queryset = self.get_queryset().filter(datasource=userdatasource)
                else:
                    raise InvestError(code=8888)
            else:
                raise InvestError(code=8888, msg='unavailable source')
            if not max_size:
                max_size = 10
            if not skip_count or skip_count < 1:
                skip_count = 0
            setrequestuser(request)
            queryset = self.filter_queryset(queryset).exclude(id=499)
            if request.user.is_anonymous:
                queryset = queryset.filter(isHidden=False,projstatus_id__in=[4,6,7,8])
                serializerclass = ProjCommonSerializer
            else:
                if request.user.has_perm('proj.admin_getproj'):
                    queryset = queryset
                    serializerclass = ProjListSerializer_admin
                else:
                    queryset = queryset.filter(Q(isHidden=False,projstatus_id__in=[4,6,7,8])| Q(createuser=request.user)| Q(supportUser=request.user)| Q(takeUser=request.user)| Q(makeUser=request.user))
                    serializerclass = ProjListSerializer_user
            count = queryset.count()
            queryset = queryset.order_by('-createdtime')[int(skip_count):int(max_size)+int(skip_count)]
            responselist = []
            for instance in queryset:
                actionlist = {'get': False, 'change': False, 'delete': False, 'canAddOrgBD':False, 'canAddMeetBD':False}
                if request.user.is_anonymous:
                    pass
                else:
                    actionlist['get'] = True
                    if request.user.has_perm('proj.admin_changeproj') or request.user.has_perm('proj.user_changeproj', instance) or request.user in [instance.takeUser, instance.makeUser, instance.supportUser]:
                        actionlist['change'] = True
                    if request.user.has_perm('proj.admin_deleteproj') or request.user.has_perm('proj.user_deleteproj',
                                                                                             instance):
                        actionlist['delete'] = True
                    if request.user.has_perm('BD.manageOrgBD') or request.user.has_perm('BD.user_addOrgBD') or request.user in [instance.takeUser, instance.makeUser]:
                        actionlist['canAddOrgBD'] = True
                    if request.user.has_perm('BD.manageMeetBD') or request.user.has_perm('BD.user_addMeetBD') or request.user in [instance.takeUser, instance.makeUser]:
                        actionlist['canAddMeetBD'] = True
                instancedata = serializerclass(instance).data
                instancedata['action'] = actionlist
                responselist.append(instancedata)
            return JSONResponse(SuccessResponse({'count': count, 'data': returnListChangeToLanguage(responselist, lang)}))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable(['proj.admin_addproj','proj.user_addproj'])
    def create(self, request, *args, **kwargs):
        try:
            projdata = request.data
            lang = request.GET.get('lang')
            projdata['createuser'] = request.user.id
            projdata['createdtime'] = datetime.datetime.now()
            projdata['datasource'] = request.user.datasource_id
            projdata['projstatus'] = 2
            tagsdata = projdata.pop('tags',None)
            industrydata = projdata.pop('industries',None)
            transactiontypedata = projdata.pop('transactionType',None)
            projAttachmentdata = projdata.pop('projAttachment',None)
            financedata = projdata.pop('finance',None)
            servicedata = projdata.pop('service',None)
            keylist = projdata.keys()
            editlist2 = [key for key in keylist if key in ['takeUser', 'makeUser', 'supportUser']]
            if len(editlist2) > 0:
                if not request.user.has_perm('proj.admin_addproj'):
                    raise InvestError(2009, msg='没有权限edit%s' % editlist2)
            with transaction.atomic():
                proj = ProjCreatSerializer(data=projdata)
                if proj.is_valid():
                    pro = proj.save()
                    if tagsdata:
                        tagslist = []
                        if not isinstance(tagslist,list):
                            raise InvestError(2007,msg='tags must be a list')
                        for tagid in tagsdata:
                            tagslist.append(projectTags(proj=pro, tag_id=tagid,createuser=request.user))
                        pro.project_tags.bulk_create(tagslist)
                    if servicedata:
                        servicelist = []
                        if not isinstance(servicedata,list):
                            raise InvestError(2007,msg='service must be an ID list')
                        for serviceid in servicedata:
                            servicelist.append(projServices(proj=pro, service_id=serviceid,createuser=request.user))
                        pro.proj_services.bulk_create(servicelist)
                    if industrydata:
                        industrylist = []
                        if not isinstance(industrydata,list):
                            raise InvestError(2007,msg='industries must be a  list')
                        for oneindustrydata in industrydata:
                            industrylist.append(projectIndustries(proj=pro, industry_id=oneindustrydata.get('industry',None),createuser=request.user,bucket=oneindustrydata.get('bucket',None),key=oneindustrydata.get('key',None)))
                        pro.project_industries.bulk_create(industrylist)
                    if transactiontypedata:
                        transactiontypelist = []
                        if not isinstance(transactiontypedata,list):
                            raise InvestError(2007,msg='transactionType must be a list')
                        for transactionPhaseid in transactiontypedata:
                            transactiontypelist.append(projectTransactionType(proj=pro, transactionType_id=transactionPhaseid,createuser=request.user))
                        pro.project_TransactionTypes.bulk_create(transactiontypelist)
                    if projAttachmentdata:
                        if not isinstance(projAttachmentdata, list):
                            raise InvestError(2007, msg='transactionType must be a list')
                        for oneprojAttachmentdata in projAttachmentdata:
                            oneprojAttachmentdata['proj'] = pro.id
                            oneprojAttachmentdata['createuser'] = request.user.id
                            projAttachmentSerializer = ProjAttachmentCreateSerializer(data=oneprojAttachmentdata)
                            if projAttachmentSerializer.is_valid():
                                projAttachmentSerializer.save()
                    if financedata:
                        if not isinstance(financedata, list):
                            raise InvestError(2007, msg='transactionType must be a list')
                        for onefinancedata in financedata:
                            onefinancedata['proj'] = pro.id
                            onefinancedata['datasource'] = request.user.datasource_id
                            onefinancedata['createuser'] = request.user.id
                            financeSerializer = FinanceCreateSerializer(data=onefinancedata)
                            if financeSerializer.is_valid():
                                financeSerializer.save()
                else:
                    raise InvestError(code=4001,
                                          msg='data有误_%s' % proj.errors)
                setUserObjectPermission(request.user, pro,
                                        ['proj.user_getproj', 'proj.user_changeproj', 'proj.user_deleteproj'])
                setUserObjectPermission(pro.supportUser, pro,
                                        ['proj.user_getproj', 'proj.user_changeproj', 'proj.user_deleteproj'])
                return JSONResponse(SuccessResponse(returnDictChangeToLanguage(ProjSerializer(pro).data,lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable()
    def retrieve(self, request, *args, **kwargs):
        try:
            lang = request.GET.get('lang')
            clienttype = request.META.get('HTTP_CLIENTTYPE')
            instance = self.get_object()
            if request.user in (instance.supportUser, instance.takeUser, instance.makeUser) or request.user.is_superuser:
                serializerclass = ProjDetailSerializer_all
            elif request.user.has_perm('proj.admin_getproj') :
                if request.user.has_perm('proj.get_secretinfo'):
                    serializerclass = ProjDetailSerializer_admin_withsecretinfo
                else:
                    serializerclass = ProjDetailSerializer_admin_withoutsecretinfo
            else:
                if request.user.has_perm('proj.get_secretinfo'):
                    serializerclass = ProjDetailSerializer_user_withsecretinfo
                else:
                    serializerclass = ProjDetailSerializer_user_withoutsecretinfo

            if instance.isHidden:
                if request.user.has_perm('proj.user_getproj', instance) or request.user.has_perm(
                        'proj.admin_getproj'):
                    pass
                else:
                    raise InvestError(code=4004, msg='没有权限查看隐藏项目')
            serializer = serializerclass(instance)
            viewprojlog(userid=request.user.id,projid=instance.id,sourceid=clienttype)
            return JSONResponse(SuccessResponse(returnDictChangeToLanguage(serializer.data,lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    def getshareprojdetail(self, request, *args, **kwargs):
        try:
            lang = request.GET.get('lang')
            clienttype = request.META.get('HTTP_CLIENTTYPE')
            tokenkey = request.GET.get('token')
            if tokenkey:
                token = ShareToken.objects.filter(key=tokenkey)
                if token.exists():
                    instance = token.first().proj
                else:
                    raise InvestError(4004,msg='token无效')
            else:
                raise InvestError(code=4004, msg='没有权限查看隐藏项目')
            serializer = ProjDetailSerializer_user_withoutsecretinfo(instance)
            viewprojlog(userid=None,projid=instance.id,sourceid=clienttype)
            return JSONResponse(SuccessResponse(returnDictChangeToLanguage(serializer.data,lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable()
    def update(self, request, *args, **kwargs):
        try:
            pro = self.get_object()
            lang = request.GET.get('lang')
            projdata = request.data
            if request.user.has_perm('proj.admin_changeproj'):
                pass
            elif request.user.has_perm('proj.user_changeproj',pro) or request.user in [pro.takeUser, pro.makeUser, pro.supportUser]:
                if projdata.get('projstatus', None) and projdata.get('projstatus', None) >= 4:
                    raise InvestError(2009,msg='只有管理员才能修改到该状态')
            else:
                raise InvestError(code=2009,msg='非上传方或管理员无法修改项目')
            projdata['lastmodifyuser'] = request.user.id
            projdata['lastmodifytime'] = datetime.datetime.now()
            projdata['datasource'] = request.user.datasource_id
            tagsdata = projdata.pop('tags', None)
            industrydata = projdata.pop('industries', None)
            transactiontypedata = projdata.pop('transactionType', None)
            projAttachmentdata = projdata.pop('projAttachment', None)
            financedata = projdata.pop('finance', None)
            servicedata = projdata.pop('service', None)
            sendmsg = False
            if projdata.get('projstatus', None) and projdata.get('projstatus', None) != pro.projstatus_id:
                if projdata.get('projstatus', None) == 4:
                    sendmsg = True
                    projdata['publishDate'] = datetime.datetime.now()
            keylist = projdata.keys()
            editlist2 = [key for key in keylist if key in ['takeUser', 'makeUser',]]
            if projdata.pop('supportUser', None):
                raise InvestError(2009, msg='上传人无法修改')
            if len(editlist2) > 0:
                if not request.user.has_perm('proj.admin_changeproj'):
                    raise  InvestError(2009,msg='没有权限修改%s'%editlist2)
            with transaction.atomic():
                proj = ProjCreatSerializer(pro,data=projdata)
                if proj.is_valid():
                    pro = proj.save()
                    if tagsdata:
                        taglist = Tag.objects.in_bulk(tagsdata)
                        addlist = [item for item in taglist if item not in pro.tags.all()]
                        removelist = [item for item in pro.tags.all() if item not in taglist]
                        pro.project_tags.filter(tag__in=removelist, is_deleted=False).update(is_deleted=True,
                                                                                           deletedtime=datetime.datetime.now(),
                                                                                           deleteduser=request.user)
                        usertaglist = []
                        for tag in addlist:
                            usertaglist.append(projectTags(proj=pro, tag_id=tag, createuser=request.user))
                        pro.project_tags.bulk_create(usertaglist)
                    if servicedata:
                        if not isinstance(servicedata, list) or len(servicedata) == 0:
                            raise InvestError(2007, msg='service must be a not null list')
                        servicelist = Service.objects.in_bulk(servicedata)
                        addlist = [item for item in servicelist if item not in pro.service.all()]
                        removelist = [item for item in pro.service.all() if item not in servicelist]
                        pro.proj_services.filter(service__in=removelist, is_deleted=False).update(is_deleted=True,
                                                                                             deletedtime=datetime.datetime.now(),
                                                                                             deleteduser=request.user)
                        projservicelist = []
                        for serviceid in addlist:
                            projservicelist.append(projServices(proj=pro, service_id=serviceid,createuser=request.user))
                        pro.proj_services.bulk_create(projservicelist)

                    if industrydata:
                        if not isinstance(industrydata, list) or len(industrydata) == 0:
                            raise InvestError(2007, msg='industrydata must be a not null list')
                        pro.project_industries.filter(is_deleted=False).update(is_deleted=True, deletedtime=datetime.datetime.now(), deleteduser=request.user)
                        for oneindustrydata in industrydata:
                            oneindustrydata['proj'] = pro.id
                            industrydataSerializer = ProjIndustryCreateSerializer(data=oneindustrydata)
                            if industrydataSerializer.is_valid():
                                industrydataSerializer.save()

                    if transactiontypedata:
                        transactionTypelist = TransactionType.objects.in_bulk(transactiontypedata)
                        addlist = [item for item in transactionTypelist if item not in pro.transactionType.all()]
                        removelist = [item for item in pro.transactionType.all() if item not in transactionTypelist]
                        pro.project_TransactionTypes.filter(transactionType__in=removelist, is_deleted=False).update(is_deleted=True,
                                                                                           deletedtime=datetime.datetime.now(),
                                                                                           deleteduser=request.user)
                        projtransactiontypelist = []
                        for transactionPhase in addlist:
                            projtransactiontypelist.append(projectTransactionType(proj=pro, transactionType_id=transactionPhase, createuser=request.user))
                        pro.project_TransactionTypes.bulk_create(projtransactiontypelist)

                    if projAttachmentdata:
                        if not isinstance(projAttachmentdata, list) or len(projAttachmentdata) == 0:
                            raise InvestError(2007, msg='transactionType must be a not null list')
                        pro.proj_attachment.filter(is_deleted=False).update(is_deleted=True, deletedtime=datetime.datetime.now(), deleteduser=request.user)
                        for oneprojAttachmentdata in projAttachmentdata:
                            oneprojAttachmentdata['proj'] = pro.id
                            projAttachmentSerializer = ProjAttachmentCreateSerializer(data=oneprojAttachmentdata)
                            if projAttachmentSerializer.is_valid():
                                projAttachmentSerializer.save()

                    if financedata:
                        if not isinstance(financedata, list):
                            raise InvestError(2007, msg='transactionType must be a not null list')
                        pro.proj_finances.filter(is_deleted=False).update(is_deleted=True, deletedtime=datetime.datetime.now(), deleteduser=request.user)
                        for onefinancedata in financedata:
                            onefinancedata['proj'] = pro.id
                            financeSerializer = FinanceCreateSerializer(data=onefinancedata)
                            if financeSerializer.is_valid():
                                financeSerializer.save()
                    cache_delete_key(self.redis_key + '_%s' % pro.id)
                else:
                    raise InvestError(code=4001,msg='data有误_%s' %  proj.errors)
                if sendmsg and not pro.ismarketplace:
                    sendmessage_projectpublish(pro, pro.supportUser,['email', 'webmsg'],sender=request.user)
                    if pro.takeUser != pro.supportUser:
                        sendmessage_projectpublish(pro, pro.takeUser, ['email', 'webmsg'], sender=request.user)
                    if pro.makeUser != pro.supportUser and pro.makeUser != pro.takeUser:
                        sendmessage_projectpublish(pro, pro.makeUser, ['email', 'webmsg'], sender=request.user)
                    pulishProjectCreateDataroom(pro, request.user)
                return JSONResponse(SuccessResponse(returnDictChangeToLanguage(ProjSerializer(pro).data,lang)))
        except InvestError as err:
                return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable()
    def sendWXGroupPdf(self, request, *args, **kwargs):
        try:
            pro = self.get_object()
            if request.user.has_perm('proj.admin_changeproj'):
                pass
            elif request.user.has_perm('proj.user_changeproj',pro) or request.user in [pro.takeUser, pro.makeUser, pro.supportUser]:
                pass
            else:
                raise InvestError(code=2009,msg='非承揽承做或上传方无法修改项目')
            if pro.projstatus_id == 4 and not pro.is_deleted:
                propath = APILOG_PATH['wxgroupsendpdf'] + pro.projtitleC + '.pdf'
                if not os.path.exists(propath):
                    self.makePdf(pro)
            else:
                raise InvestError(2007,msg='不满足发送条件')
            return JSONResponse(SuccessResponse({"status":'发送中，请稍后'}))
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
            if request.user.has_perm('proj.admin_deleteproj'):
                pass
            elif request.user.has_perm('proj.user_deleteproj',instance) or request.user in [instance.takeUser, instance.makeUser, instance.supportUser]:
                if instance.projstatus_id >= 4:
                    raise InvestError(2009, msg='没有权限，请联系管理员删除')
            else:
                raise InvestError(code=2009)
            if instance.proj_datarooms.filter(is_deleted=False,proj=instance).exists():
                raise InvestError(code=2010, msg=u'{} 上有关联数据'.format('proj_datarooms'))
            with transaction.atomic():
                for link in ['proj_timelines', 'proj_finances', 'proj_attachment', 'project_tags', 'project_industries', 'project_TransactionTypes',
                             'proj_favorite', 'proj_sharetoken', 'proj_datarooms', 'proj_services', 'proj_schedule', 'proj_orgBDs']:
                    if link in ['proj_timelines']:
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
                                    raise InvestError(code=2010, msg=u'{} 上有关联数据'.format(link))
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
                instance.deletetime = datetime.datetime.now()
                instance.save()
                cache_delete_key(self.redis_key + '_%s' % instance.id)
                return JSONResponse(SuccessResponse(returnDictChangeToLanguage(ProjSerializer(instance).data,lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @detail_route(methods=['get'])
    @loginTokenIsAvailable()
    def getshareprojtoken(self, request, *args, **kwargs):
        try:
            proj = self.get_object()
            with transaction.atomic():
                sharetokenset = ShareToken.objects.filter(user=request.user,proj=proj,created__gt=(datetime.datetime.now()-datetime.timedelta(hours=1 * 1)))
                if sharetokenset.exists():
                    sharetoken = sharetokenset.last()
                else:
                    sharetoken = ShareToken(user=request.user,proj=proj)
                    sharetoken.save()
                return JSONResponse(SuccessResponse(sharetoken.key))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @detail_route(methods=['get'])
    def sendPDF(self, request, *args, **kwargs):
        try:
            request.user = checkrequesttoken(request.GET.get('acw_tk'))
            lang = request.GET.get('lang','cn')
            proj = self.get_object()
            if proj.isHidden:
                if request.user.has_perm('proj.admin_getproj'):
                    pass
                elif request.user in [proj.createuser,proj.takeUser,proj.makeUser,proj.supportUser]:
                    pass
                else:
                    raise InvestError(2009,msg='隐藏项目，只有项目承揽承做及上传方可以获取相关项目信息')
            options = {
                'dpi': 1400,
                'page-size': 'A4',
                'margin-top': '0in',
                'margin-right': '0in',
                'margin-bottom': '0in',
                'margin-left': '0in',
                'encoding': "UTF-8",
                'no-outline': None,
            }
            pdfpath = APILOG_PATH['pdfpath_base'] + 'P' + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.pdf'
            config = pdfkit.configuration(wkhtmltopdf=APILOG_PATH['wkhtmltopdf'])
            aaa = pdfkit.from_url(PROJECTPDF_URLPATH + str(proj.id)+'&lang=%s'%lang, pdfpath, configuration=config, options=options)
            out_path = addWaterMark(pdfpath,watermarkcontent=[request.user.usernameC, request.user.org.orgnameC if request.user.org else request.user.email, request.user.email])
            if aaa:
                fn = open(out_path, 'rb')
                response = StreamingHttpResponse(file_iterator(fn))
                response['Content-Type'] = 'application/octet-stream'
                response["content-disposition"] = 'attachment;filename=%s.pdf'% (proj.projtitleC.encode('utf-8') if lang == 'cn' else proj.projtitleE)
                os.remove(out_path)
            else:
                raise InvestError(50010,msg='pdf生成失败')
            return response
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    def makePdf(self, proj):
        try:
            options = {
                'dpi': 1400,
                'page-size': 'A4',
                'margin-top': '0in',
                'margin-right': '0in',
                'margin-bottom': '0in',
                'margin-left': '0in',
                'encoding': "UTF-8",
                'no-outline': None,
            }
            pdfpath = APILOG_PATH['wxgroupsendpdf'] + proj.projtitleC.replace('/','-') + '.pdf'
            config = pdfkit.configuration(wkhtmltopdf=APILOG_PATH['wkhtmltopdf'])
            aaa = pdfkit.from_url(PROJECTPDF_URLPATH + str(proj.id) + '&lang=cn', pdfpath, configuration=config,
                                  options=options)
            if not aaa:
                raise InvestError(2007,msg='生成项目pdf失败')
            if proj.country_id == 42 and proj.currency_id == 1:
                amount_field, currency, currencytype = 'financeAmount', '￥', 'CNY'
            else:
                amount_field, currency, currencytype = 'financeAmount_USD', '$', 'USD'

            f = open(APILOG_PATH['wxgroupsendpdf'] + '/projdesc.txt', 'a')
            content = {proj.projtitleC.split('：')[0]: '本周项目自动推送：%s%s' % (proj.projtitleC.split('：')[-1],
                                       ('，拟交易规模：%s%s %s' % (currency, '{:,}'.format(getattr(proj,amount_field)) if getattr(proj,amount_field) else 'N/A', currencytype)))}
            f.writelines(json.dumps(content, ensure_ascii=False))
            f.writelines('\n')
            f.close()
        except Exception:
            logexcption()


class ProjAttachmentView(viewsets.ModelViewSet):
    """
    list:获取项目附件
    create:创建项目附件 （projid+data）
    update:修改项目附件（批量idlist+data）
    destroy:删除项目附件 （批量idlist）
    """
    filter_backends = (filters.DjangoFilterBackend,)
    queryset = attachment.objects.all().filter(is_deleted=False)
    filter_fields = ('proj',)
    serializer_class = ProjAttachmentSerializer



    def get_queryset(self):
        assert self.queryset is not None, (
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method."
            % self.__class__.__name__
        )
        queryset = self.queryset
        if isinstance(queryset, QuerySet):
            if self.request.user.is_authenticated:
                queryset = queryset.filter(proj__datasource=self.request.user.datasource)
            else:
                queryset = queryset.all()
        else:
            raise InvestError(code=8890)
        return queryset

    def get_object(self, pk=None):
        if pk:

            try:
                obj = self.queryset.get(id=pk)
            except attachment.DoesNotExist:
                raise InvestError(code=40031)
        else:
            lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
            assert lookup_url_kwarg in self.kwargs, (
                'Expected view %s to be called with a URL keyword argument '
                'named "%s". Fix your URL conf, or set the `.lookup_field` '
                'attribute on the view correctly.' %
                (self.__class__.__name__, lookup_url_kwarg)
            )
            try:
                obj = self.queryset.get(id=self.kwargs[lookup_url_kwarg])
            except attachment.DoesNotExist:
                raise InvestError(code=40031)
        if obj.proj.datasource != self.request.user.datasource:
            raise InvestError(code=8888)
        return obj
    def get_proj(self,pk):
        obj = read_from_cache('project_%s' % pk)
        if not obj:
            try:
                obj = project.objects.get(id=pk, is_deleted=False)
            except project.DoesNotExist:
                raise InvestError(code=4002)
            else:
                write_to_cache('project_%s' % pk, obj)
        if obj.datasource != self.request.user.datasource:
            raise InvestError(code=8888)
        if obj.is_deleted:
            raise InvestError(code=4002,msg='项目已删除')
        return obj
    @loginTokenIsAvailable()
    def list(self, request, *args, **kwargs):
        try:
            page_size = request.GET.get('page_size', 10)
            page_index = request.GET.get('page_index', 1)
            lang = request.GET.get('lang', 'cn')
            projid = request.GET.get('proj')
            if projid:
                proj = self.get_proj(projid)
            else:
                raise InvestError(2007,msg='proj 不能为空')
            queryset = self.filter_queryset(self.get_queryset())
            if not request.user.has_perm('proj.admin_getproj'):
                queryset = queryset
            else:
                queryset = queryset.filter(proj=proj)
            try:
                count = queryset.count()
                queryset = Paginator(queryset, page_size)
                queryset = queryset.page(page_index)
            except EmptyPage:
                return JSONResponse(SuccessResponse([],msg='没有符合的结果'))
            serializer = ProjAttachmentSerializer(queryset, many=True)
            return JSONResponse(SuccessResponse({'count':count,'data':returnListChangeToLanguage(serializer.data,lang)}))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable()
    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            projid = data.get('proj')
            lang = request.GET.get('lang')
            proj = self.get_proj(projid)
            if request.user.has_perm('proj.admin_changeproj'):
                pass
            elif request.user.has_perm('proj.user_changeproj',proj):
                pass
            elif request.user in [proj.createuser,proj.takeUser,proj.makeUser,proj.supportUser]:
                pass
            else:
                raise InvestError(code=2009,msg='没有增加该项目附件的权限')
            with transaction.atomic():
                data['createuser'] = request.user.id
                attachments = ProjAttachmentCreateSerializer(data=data)
                if attachments.is_valid():
                    attachments.save()
                else:
                    raise InvestError(code=4001,msg='附件信息有误_%s\n%s' % (attachments.error_messages, attachments.errors))
                return JSONResponse(SuccessResponse(returnListChangeToLanguage(attachments.data,lang)))
        except InvestError as err:
                return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable()
    def update(self, request, *args, **kwargs):
        data = request.data
        lang = request.GET.get('lang')
        attachmentdata = data.get('attachment')
        try:
            with transaction.atomic():
                if attachmentdata:
                    newfinances = []
                    for f in attachmentdata:
                        fid = f['id']
                        if not isinstance(fid,(int,str,unicode)) or not fid:
                            raise InvestError(2007,msg='attachment[\'id\'] must be a int/str type')
                        projAttachment = self.get_object(fid)
                        if request.user.has_perm('proj.admin_changeproj'):
                            pass
                        elif request.user.has_perm('proj.user_changeproj',projAttachment.proj):
                            pass
                        elif request.user in [projAttachment.proj.createuser, projAttachment.proj.takeUser, projAttachment.proj.makeUser, projAttachment.proj.supportUser]:
                            pass
                        else:
                            raise InvestError(code=2009)
                        f['lastmodifyuser'] = request.user.id
                        f['lastmodifytime'] = datetime.datetime.now()
                        attachmentSer = ProjAttachmentCreateSerializer(projAttachment,data=attachmentdata)
                        if attachmentSer.is_valid():
                            attachmentSer.save()
                        else:
                            raise InvestError(code=4001,
                                          msg='财务信息有误_%s\n%s' % (attachmentSer.error_messages, attachmentSer.errors))
                        newfinances.append(attachmentSer.data)
                else:
                    raise InvestError(code=20071, msg='finances field cannot be null')
                return JSONResponse(SuccessResponse(returnListChangeToLanguage(newfinances, lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable()
    def destroy(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                attachmentidlist = request.data.get('attachment',None)
                if not isinstance(attachmentidlist,list) or not attachmentidlist:
                    raise InvestError(code=20071,msg='\'attachment\' expect an not null list')
                lang = request.GET.get('lang')
                returnlist = []
                for projattachmentid in attachmentidlist:
                    projattachment = self.get_object(projattachmentid)
                    if request.user.has_perm('proj.user_changeproj', projattachment.proj):
                        pass
                    elif request.user in [projattachment.proj.createuser, projattachment.proj.takeUser,
                                          projattachment.proj.makeUser, projattachment.proj.supportUser]:
                        pass
                    elif request.user.has_perm('proj.admin_changeproj'):
                        pass
                    else:
                        raise InvestError(code=2009, msg='没有权限')
                    projattachment.is_deleted = True
                    projattachment.deleteduser = request.user
                    projattachment.deletedtime = datetime.datetime.now()
                    projattachment.save()
                    deleteqiniufile(projattachment.bucket, projattachment.key)
                    deleteqiniufile(projattachment.bucket, projattachment.realfilekey)
                    returnlist.append(ProjAttachmentSerializer(projattachment).data)
                return JSONResponse(SuccessResponse(returnListChangeToLanguage(returnlist,lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))



class ProjFinanceView(viewsets.ModelViewSet):
    """
    list:获取财务信息
    create:创建财务信息 （projid+data）
    update:修改财务信息（批量idlist+data）
    destroy:删除财务信息 （批量idlist）
    """
    filter_backends = (filters.DjangoFilterBackend,)
    queryset = finance.objects.all().filter(is_deleted=False)
    filter_fields = ('proj',)
    serializer_class = FinanceSerializer



    def get_queryset(self):
        assert self.queryset is not None, (
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method."
            % self.__class__.__name__
        )
        queryset = self.queryset
        if isinstance(queryset, QuerySet):
            if self.request.user.is_authenticated:
                queryset = queryset.filter(datasource=self.request.user.datasource)
            else:
                queryset = queryset.all()
        else:
            raise InvestError(code=8890)
        return queryset

    def get_object(self, pk=None):
        if pk:

            try:
                obj = self.queryset.get(id=pk)
            except finance.DoesNotExist:
                raise InvestError(code=40031)
        else:
            lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
            assert lookup_url_kwarg in self.kwargs, (
                'Expected view %s to be called with a URL keyword argument '
                'named "%s". Fix your URL conf, or set the `.lookup_field` '
                'attribute on the view correctly.' %
                (self.__class__.__name__, lookup_url_kwarg)
            )
            try:
                obj = self.queryset.get(id=self.kwargs[lookup_url_kwarg])
            except finance.DoesNotExist:
                raise InvestError(code=40031)
        if obj.datasource != self.request.user.datasource:
            raise InvestError(code=8888)
        return obj
    def get_proj(self,pk):
        obj = read_from_cache('project_%s' % pk)
        if not obj:
            try:
                obj = project.objects.get(id=pk, is_deleted=False)
            except project.DoesNotExist:
                raise InvestError(code=4002)
            else:
                write_to_cache('project_%s' % pk, obj)
        if obj.datasource != self.request.user.datasource:
            raise InvestError(code=8888)
        if obj.is_deleted:
            raise InvestError(code=4002,msg='项目已删除')
        return obj

    @loginTokenIsAvailable()
    def list(self, request, *args, **kwargs):
        try:
            page_size = request.GET.get('page_size', 10)
            page_index = request.GET.get('page_index', 1)
            lang = request.GET.get('lang', 'cn')
            projid = request.GET.get('proj')
            if projid and isinstance(projid,(str,int,unicode)):
                proj = self.get_proj(projid)
            else:
                raise InvestError(2007, msg='proj 不能为空')
            queryset = self.filter_queryset(self.get_queryset())
            if not proj.financeIsPublic:
                if request.user in (proj.supportUser, proj.takeUser, proj.makeUser) or request.user.is_superuser:
                    pass
                elif request.user.has_perm('proj.admin_getproj'):
                    pass
                else:
                    return JSONResponse(SuccessResponse({'count':0,'data':[]}, msg='没有符合的结果'))
            try:
                count = queryset.count()
                queryset = Paginator(queryset, page_size)
                queryset = queryset.page(page_index)
            except EmptyPage:
                return JSONResponse(SuccessResponse({'count':0,'data':[]}, msg='没有符合的结果'))
            serializer = FinanceSerializer(queryset, many=True)
            return JSONResponse(SuccessResponse({'count':count,'data':returnListChangeToLanguage(serializer.data,lang)}))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable()
    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            projid = data.get('proj')
            proj = self.get_proj(projid)
            if request.user.has_perm('proj.admin_changeproj'):
                pass
            elif request.user.has_perm('proj.user_changeproj',proj):
                pass
            elif request.user in [proj.createuser, proj.takeUser,
                                  proj.makeUser, proj.supportUser]:
                pass
            else:
                raise InvestError(code=2009,msg='没有增加该项目财务信息的权限')
            lang = request.GET.get('lang')
            with transaction.atomic():

                data['createuser'] = request.user.id
                data['datasource'] = request.user.datasource.id
                finances = FinanceCreateSerializer(data=data)
                if finances.is_valid():
                    finances.save()
                else:
                    raise InvestError(code=4001,msg='财务信息有误_%s\n%s' % (finances.error_messages, finances.errors))
                return JSONResponse(SuccessResponse(returnListChangeToLanguage(finances.data,lang)))
        except InvestError as err:
                return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable()
    def update(self, request, *args, **kwargs):
        data = request.data
        lang = request.GET.get('lang')
        financedata = data.get('finances')
        try:
            with transaction.atomic():
                if financedata:
                    newfinances = []
                    for f in financedata:
                        fid = f['id']
                        f.pop('proj')
                        if not isinstance(fid,(int,str,unicode)) or not fid:
                            raise InvestError(2007,msg='finances[\'id\'] must be a int/str type')
                        projfinance = self.get_object(fid)
                        if request.user.has_perm('proj.admin_changeproj'):
                            pass
                        elif request.user.has_perm('proj.user_changeproj',projfinance.proj):
                            pass
                        elif request.user in [projfinance.proj.createuser, projfinance.proj.takeUser, projfinance.proj.makeUser, projfinance.proj.supportUser]:
                            pass
                        else:
                            raise InvestError(code=2009,msg='没有权限修改项目（%s）的相关信息'%projfinance.proj)
                        f['lastmodifyuser'] = request.user.id
                        f['lastmodifytime'] = datetime.datetime.now()
                        finance = FinanceChangeSerializer(projfinance,data=f)
                        if finance.is_valid():
                            finance.save()
                        else:
                            raise InvestError(code=4001,
                                          msg='财务信息有误_%s\n%s' % (finance.error_messages, finance.errors))
                        newfinances.append(finance.data)
                else:
                    raise InvestError(code=20071, msg='finances field cannot be null')
                return JSONResponse(SuccessResponse(returnListChangeToLanguage(newfinances, lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable()
    def destroy(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                financeidlist = request.data.get('finances',None)
                if not isinstance(financeidlist,list) or not financeidlist:
                    raise InvestError(code=20071,msg='\'finances\' expect an not null list')
                lang = request.GET.get('lang')
                returnlist = []
                for projfinanceid in financeidlist:
                    projfinance = self.get_object(projfinanceid)
                    if request.user.has_perm('proj.user_changeproj', projfinance.proj):
                        pass
                    elif request.user in [projfinance.proj.createuser, projfinance.proj.takeUser,
                                          projfinance.proj.makeUser, projfinance.proj.supportUser]:
                        pass
                    elif request.user.has_perm('proj.admin_changeproj'):
                        pass
                    else:
                        raise InvestError(code=2009, msg='没有权限')
                    projfinance.is_deleted = True
                    projfinance.deleteduser = request.user
                    projfinance.deletedtime = datetime.datetime.now()
                    projfinance.save()
                    returnlist.append(FinanceSerializer(projfinance).data)
                return JSONResponse(SuccessResponse(returnListChangeToLanguage(returnlist,lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))


class ProjectFavoriteView(viewsets.ModelViewSet):
    """
    list:获取收藏
    create:增加收藏
    destroy:删除收藏
    """
    filter_backends = (filters.DjangoFilterBackend,)
    queryset = favoriteProject.objects.filter(is_deleted=False)
    filter_fields = ('user','trader','favoritetype','proj')
    serializer_class = FavoriteSerializer
    Model = favoriteProject

    def get_queryset(self):
        assert self.queryset is not None, (
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method."
            % self.__class__.__name__
        )
        queryset = self.queryset
        if isinstance(queryset, QuerySet):
            if self.request.user.is_authenticated:
                queryset = queryset.filter(datasource=self.request.user.datasource)
            else:
                queryset = queryset.all()
        else:
            raise InvestError(code=8890)
        return queryset

    def get_object(self, pk=None):
        if pk:
            try:
                obj = self.queryset.get(id=pk)
            except finance.DoesNotExist:
                raise InvestError(code=4006)
        else:
            lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
            assert lookup_url_kwarg in self.kwargs, (
                'Expected view %s to be called with a URL keyword argument '
                'named "%s". Fix your URL conf, or set the `.lookup_field` '
                'attribute on the view correctly.' %
                (self.__class__.__name__, lookup_url_kwarg)
            )
            try:
                obj = self.queryset.get(id=self.kwargs[lookup_url_kwarg])
            except finance.DoesNotExist:
                raise InvestError(code=4006)
        if obj.datasource != self.request.user.datasource:
            raise InvestError(code=8888)
        return obj

    def get_user(self,pk):
        obj = read_from_cache('user_%s' % pk)
        if not obj:
            try:
                obj = MyUser.objects.get(id=pk, is_deleted=False)
            except MyUser.DoesNotExist:
                raise InvestError(code=2002)
            else:
                write_to_cache('user_%s' % pk, obj)
        if obj.datasource != self.request.user.datasource:
            raise InvestError(code=8888)
        if obj.is_deleted:
            raise InvestError(code=2002,msg='用户已删除')
        return obj

    #获取收藏列表，GET参数'user'，'trader'，'favoritetype'
    @loginTokenIsAvailable()
    def list(self, request, *args, **kwargs):
        try:
            page_size = request.GET.get('page_size', 10)
            page_index = request.GET.get('page_index', 1)
            lang = request.GET.get('lang', 'cn')
            userid = request.GET.get('user')
            traderid = request.GET.get('trader')
            queryset = self.filter_queryset(self.get_queryset())
            sort = request.GET.get('sort')
            if sort not in ['True', 'true', True, 1, 'Yes', 'yes', 'YES', 'TRUE']:
                queryset = queryset.order_by('-createdtime',)
            else:
                queryset = queryset.order_by('createdtime',)
            if request.user.has_perm('proj.admin_getfavorite'):
                pass
            else:
                if not userid and not traderid:
                    queryset = queryset.filter(Q(user=request.user) |Q(trader=request.user))
                elif userid and not traderid:
                    user = self.get_user(userid)
                    if not request.user.has_perm('usersys.user_getfavorite',user):
                        raise InvestError(code=2009)
                    else:
                        queryset = queryset.filter(Q(trader=request.user) | Q(trader=None))
                elif not userid and traderid:
                    queryset = queryset.filter(user=request.user,trader_id=traderid)
                else:
                    if userid == request.user.id or traderid == request.user.id:
                        pass
                    else:
                        raise InvestError(code=2009)
            try:
                count = queryset.count()
                queryset = Paginator(queryset, page_size)
                queryset = queryset.page(page_index)
            except EmptyPage:
                return JSONResponse(SuccessResponse({'count': 0, 'data': []}))
            serializer = FavoriteSerializer(queryset, many=True)
            return JSONResponse(SuccessResponse({'count':count,'data':returnListChangeToLanguage(serializer.data,lang)}))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    # 批量增加，接受modeldata，proj=projs=projidlist
    @loginTokenIsAvailable()
    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            lang = request.GET.get('lang')
            userid = data.get('user',None)
            ftype = data.get('favoritetype',None)
            if not userid or not ftype:
                raise InvestError(20071,msg='user/favoritetype cannot be null')
            data['createuser'] = request.user.id
            data['datasource'] = request.user.datasource.id
            projidlist = data.pop('projs',None)
            user = self.get_user(userid)
            push_alias = None
            pushcontent = None
            if ftype == 4:
                pass
            elif ftype == 5:
                traderid = data.get('trader', None)
                if not traderid:
                    raise InvestError(4005,msg='trader cannot be null')
                traderuser = self.get_user(traderid)
                if not user.has_perm('usersys.user_interestproj', traderuser):
                    raise InvestError(code=4005)
                push_alias = traderuser.id
                pushcontent = '投资人%s对%s个项目感兴趣，请尽快联系'%(request.user.usernameC,len(projidlist))
            elif ftype in [1,2]:
                if not request.user.has_perm('proj.admin_addfavorite'):
                    raise InvestError(code=4005)
            elif ftype == 3:
                if not request.user.has_perm('usersys.user_addfavorite', user):
                    raise InvestError(code=4005)
                push_alias = user.id
                pushcontent = '交易师(%s)给您推荐%s个项目'%(request.user.usernameC,len(projidlist))
            else:
                raise InvestError(code=2009)
            with transaction.atomic():
                favoriteProjectList = []
                projlist = []
                for projid in projidlist:
                    data['proj'] = projid
                    newfavorite = FavoriteCreateSerializer(data=data)
                    if newfavorite.is_valid():
                        newfavoriteproj = newfavorite.save()
                        if newfavoriteproj.user.datasource != request.user.datasource or newfavoriteproj.proj.datasource != request.user.datasource or\
                                (newfavoriteproj.trader and newfavoriteproj.trader.datasource != request.user.datasource):
                            raise InvestError(code=8888)
                        favoriteProjectList.append(newfavorite.data)
                        projlist.append(newfavoriteproj)
                    else:
                        raise InvestError(code=20071,msg='%s'%newfavorite.errors)
                for proj in projlist:
                    if ftype == 5:
                        receiver = proj.trader
                    else:
                        receiver = proj.user
                    sendmessage_favoriteproject(proj, receiver, sender=request.user)
                if push_alias:
                    pushnotification(receiver_alias=push_alias,content=pushcontent,bdage=1)
                return JSONResponse(SuccessResponse(returnListChangeToLanguage(favoriteProjectList,lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    #批量删除（参数传收藏model的idlist）
    @loginTokenIsAvailable()
    def destroy(self, request, *args, **kwargs):
        try:
            favoridlist = request.data.get('favoriteids')
            favorlist = []
            lang = request.GET.get('lang')
            if not isinstance(favoridlist,list) or not favoridlist:
                raise InvestError(code=20071, msg='accept a not null list')
            with transaction.atomic():
                for favorid in favoridlist:
                    instance = self.get_object(favorid)
                    if request.user.has_perm('proj.admin_deletefavorite') or request.user == instance.user:
                        pass
                    else:
                        raise InvestError(code=2009)
                    instance.is_deleted = True
                    instance.deleteduser = request.user
                    instance.deletedtime = datetime.datetime.now()
                    instance.save()
                    favorlist.append(FavoriteSerializer(instance).data)
                return JSONResponse(SuccessResponse(returnListChangeToLanguage(favorlist, lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))


def testPdf(request):
    projid = request.GET.get('id')
    lang = request.GET.get('lang', 'cn')
    proj = project.objects.get(id=projid)
    aaa = {
        'project': ProjDetailSerializer_user_withoutsecretinfo(proj).data,
        'finance': FinanceSerializer(proj.proj_finances.filter(is_deleted=False), many=True).data
    }
    if lang == 'cn':
        res = render(request, 'proj_template_cn.html', aaa)
    else:
        res = render(request, 'proj_template_en.html', aaa)
    return HttpResponse(res)

