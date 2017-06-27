#coding=utf-8
import traceback
from django.core.paginator import Paginator, EmptyPage
from django.db import models,transaction
from django.db.models import Q,QuerySet
from django.core.exceptions import FieldDoesNotExist
from django.db.models.fields.reverse_related import ForeignObjectRel
from guardian.shortcuts import assign_perm
from rest_framework import filters, viewsets
import datetime

from rest_framework.decorators import detail_route

from APIlog.views import viewprojlog
from proj.models import project, finance, projectTags, projectIndustries, projectTransactionType, favoriteProject, \
    ShareToken, attachment
from proj.serializer import ProjSerializer, FinanceSerializer, ProjCreatSerializer, \
    ProjCommonSerializer, FinanceChangeSerializer, FinanceCreateSerializer, FavoriteSerializer, FavoriteCreateSerializer,ProjAttachmentSerializer
from sourcetype.models import Tag, Industry, TransactionType, DataSource
from third.views.qiniufile import deleteqiniufile
from usersys.models import MyUser
from utils.sendMessage import sendmessage_projectauditstatuchange
from utils.util import catchexcption, read_from_cache, write_to_cache, loginTokenIsAvailable, returnListChangeToLanguage, \
    returnDictChangeToLanguage, SuccessResponse, InvestErrorResponse, ExceptionResponse, setrequestuser, \
    setUserObjectPermission
from utils.customClass import JSONResponse, InvestError, RelationFilter

from django_filters import FilterSet

class ProjectFilter(FilterSet):
    industrys = RelationFilter(filterstr='industry',lookup_method='in')
    tags = RelationFilter(filterstr='tags',lookup_method='in')
    projstatus = RelationFilter(filterstr='projstatus',lookup_method='in')
    country = RelationFilter(filterstr='country',lookup_method='in')
    netIncome_USD_F = RelationFilter(filterstr='proj_finances__netIncome_USD',lookup_method='gte')
    netIncome_USD_T = RelationFilter(filterstr='proj_finances__netIncome_USD', lookup_method='lte')
    grossProfit_F = RelationFilter(filterstr='proj_finances__grossProfit', lookup_method='gte')
    grossProfit_T = RelationFilter(filterstr='proj_finances__grossProfit', lookup_method='lte')
    class Meta:
        model = project
        fields = ('isoverseasproject','industries','tags','projstatus','country','netIncome_USD_F','netIncome_USD_T','grossProfit_F','grossProfit_T')


class ProjectView(viewsets.ModelViewSet):
    """
    list:获取项目列表
    create:创建项目
    retrieve:获取项目详情
    update:修改项目
    destroy:删除项目
    getshareprojtoken:获取分享项目token
    getshareproj:获取分享的项目详情
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
            raise InvestError(code=8888,msg='资源非同源')
        return obj

    def list(self, request, *args, **kwargs):
        try:
            page_size = request.GET.get('page_size')
            page_index = request.GET.get('page_index')  # 从第一页开始
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
                raise InvestError(code=8888, msg='source field is required')
            if not page_size:
                page_size = 10
            if not page_index:
                page_index = 1
            setrequestuser(request)
            queryset = self.filter_queryset(queryset)
            if request.user.is_anonymous:
                queryset = queryset.filter(isHidden=False)
                serializerclass = ProjCommonSerializer
            else:
                if request.user.has_perm('proj.admin_getproj'):
                    queryset = queryset
                    serializerclass = ProjCreatSerializer
                else:
                    queryset = queryset.filter(Q(isHidden=False) | Q(createuser=request.user))
                    serializerclass = ProjCommonSerializer
            try:
                count = queryset.count()
                queryset = Paginator(queryset, page_size)
            except EmptyPage:
                return JSONResponse(SuccessResponse([],msg='没有符合条件的结果'))
            queryset = queryset.page(page_index)
            actionlist = {'get': False, 'change': False, 'delete': False}
            responselist = []
            for instance in queryset:
                if request.user.is_anonymous:
                    pass
                else:
                    actionlist['get'] = True
                    if request.user.has_perm('proj.admin_changeproj') or request.user.has_perm('proj.user_changeproj',
                                                                                             instance):
                        actionlist['change'] = True
                    if request.user.has_perm('proj.admin_deleteproj') or request.user.has_perm('proj.user_deleteproj',
                                                                                             instance):
                        actionlist['delete'] = True
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
            tagsdata = projdata.pop('tags',None)
            industrydata = projdata.pop('industries',None)
            transactiontypedata = projdata.pop('transactionType',None)
            projAttachmentdata = projdata.pop('projAttachment',None)
            financedata = projdata.pop('finance',None)
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
                    if industrydata:
                        industrylist = []
                        if not isinstance(industrydata,list):
                            raise InvestError(2007,msg='industries must be a  list')
                        for industryid in industrydata:
                            industrylist.append(projectIndustries(proj=pro, industry_id=industryid,createuser=request.user))
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
                            projAttachmentSerializer = ProjAttachmentSerializer(data=oneprojAttachmentdata)
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
            if request.user.has_perm('proj.admin_getproj'):
                serializerclass = ProjSerializer
            else:
                serializerclass = ProjSerializer
            instance = self.get_object()
            if instance.isHidden:
                if not request.user.has_perm('proj.user_getproj', instance) or not request.user.has_perm(
                        'proj.admin_getproj'):
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
            if tokenkey and isinstance(tokenkey,str):
                token = ShareToken.objects.get(key=tokenkey)
                instance = token.proj
            else:
                raise InvestError(code=4004, msg='没有权限查看隐藏项目')
            serializer = ProjSerializer(instance)
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
            if request.user.has_perm('proj.admin_changeproj'):
                pass
            elif request.user.has_perm('proj.user_changeproj',pro):
                pass
            else:
                raise InvestError(code=2009,msg='非上传方或管理员无法修改项目')
            projdata = request.data
            projdata['lastmodifyuser'] = request.user.id
            projdata['lastmodifytime'] = datetime.datetime.now()
            projdata['datasource'] = request.user.datasource_id
            tagsdata = projdata.pop('tags', None)
            industrydata = projdata.pop('industries', None)
            transactiontypedata = projdata.pop('transactionType', None)
            projAttachmentdata = projdata.pop('projAttachment', None)
            financedata = projdata.pop('finance', None)
            sendmessage = False
            if projdata.get('projstatus', None) and projdata.get('projstatus', None) != pro.projstatus_id:
                sendmessage = True
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

                    if industrydata:
                        industrylist = Industry.objects.in_bulk(industrydata)
                        addlist = [item for item in industrylist if item not in pro.industries.all()]
                        removelist = [item for item in pro.industries.all() if item not in industrylist]
                        pro.project_industries.filter(industry__in=removelist, is_deleted=False).update(is_deleted=True,
                                                                                           deletedtime=datetime.datetime.now(),
                                                                                           deleteduser=request.user)
                        projindustrylist = []
                        for industry in addlist:
                            projindustrylist.append(projectIndustries(proj=pro, industry_id=industry, createuser=request.user))
                        pro.project_industries.bulk_create(projindustrylist)

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
                        if not isinstance(projAttachmentdata, list):
                            raise InvestError(2007, msg='transactionType must be a not null list')
                        pro.proj_attachment.update(is_deleted=True, deletedtime=datetime.datetime.now(), deleteduser=request.user)
                        for oneprojAttachmentdata in projAttachmentdata:
                            oneprojAttachmentdata['proj'] = pro.id
                            projAttachmentSerializer = ProjAttachmentSerializer(data=oneprojAttachmentdata)
                            if projAttachmentSerializer.is_valid():
                                projAttachmentSerializer.save()

                    if financedata:
                        if not isinstance(financedata, list):
                            raise InvestError(2007, msg='transactionType must be a not null list')
                        pro.proj_finances.update(is_deleted=True, deletedtime=datetime.datetime.now(), deleteduser=request.user)
                        for onefinancedata in financedata:
                            onefinancedata['proj'] = pro.id
                            financeSerializer = FinanceCreateSerializer(data=onefinancedata)
                            if financeSerializer.is_valid():
                                financeSerializer.save()

                else:
                    raise InvestError(code=4001,msg='data有误_%s' %  proj.errors)
                if sendmessage:
                    sendmessage_projectauditstatuchange(pro,pro.supportUser,['app','email','webmsg'],sender=request.user)
                return JSONResponse(SuccessResponse(returnDictChangeToLanguage(ProjSerializer(pro).data,lang)))
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
            elif request.user.has_perm('proj.user_deleteproj',instance):
                pass
            else:
                raise InvestError(code=2009)
            with transaction.atomic():
                rel_fileds = [f for f in instance._meta.get_fields() if isinstance(f, ForeignObjectRel)]
                links = [f.get_accessor_name() for f in rel_fileds]
                for link in links:
                    if link in []:
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
                                manager.delete()
                        else:
                            try:
                                manager.model._meta.get_field('is_deleted')
                                if manager.all().filter(is_deleted=False).count():
                                    manager.all().update(is_deleted=True)
                            except FieldDoesNotExist:
                                if manager.all().count():
                                    manager.all().delete()
                instance.is_deleted = True
                instance.deleteduser = request.user
                instance.deletetime = datetime.datetime.now()
                instance.save()
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
    redis_key = 'projectAttachment'
    Model = finance


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
            obj = read_from_cache(self.redis_key + '_%s' % pk)
            if not obj:
                try:
                    obj = self.queryset.get(id=pk)
                except attachment.DoesNotExist:
                    raise InvestError(code=40031)
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
                except attachment.DoesNotExist:
                    raise InvestError(code=40031)
                else:
                    write_to_cache(self.redis_key + '_%s' % self.kwargs[lookup_url_kwarg], obj)
        if obj.proj.datasource != self.request.user.datasource:
            raise InvestError(code=8888, msg='资源非同源')
        return obj

    @loginTokenIsAvailable()
    def list(self, request, *args, **kwargs):
        try:
            page_size = request.GET.get('page_size')
            page_index = request.GET.get('page_index')  # 从第一页开始
            lang = request.GET.get('lang')
            if not page_size:
                page_size = 10
            if not page_index:
                page_index = 1
            queryset = self.filter_queryset(self.get_queryset())
            if not request.user.has_perm('proj.admin_getproj'):
                queryset = queryset
            else:
                queryset = queryset.filter(proj__createuser__id=request.user.id)
            try:
                count = queryset.count()
                queryset = Paginator(queryset, page_size)
            except EmptyPage:
                return JSONResponse(SuccessResponse([],msg='没有符合的结果'))
            queryset = queryset.page(page_index)
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
            try:
                proj = project.objects.get(id=projid,is_deleted=False,datasource=request.user.datasource)
            except project.DoesNotExist:
                raise InvestError(code=4002,msg='指定内容不存在')
            if request.user.has_perm('proj.admin_changeproj'):
                pass
            elif request.user.has_perm('proj.user_changeproj',proj):
                pass
            else:
                raise InvestError(code=2009,msg='没有增加该项目附件的权限')
            lang = request.GET.get('lang')
            attachmentdata = data.get('attachment')
            with transaction.atomic():
                if attachmentdata:
                    for f in attachmentdata:
                        f['proj'] = proj.pk
                        f['createuser'] = request.user.id
                    attachments = ProjAttachmentSerializer(data=attachmentdata,many=True)
                    if attachments.is_valid():
                        attachments.save()
                    else:
                        raise InvestError(code=4001,msg='财务信息有误_%s\n%s' % (attachments.error_messages, attachments.errors))
                else:
                    raise InvestError(code=20071,msg='attachment field cannot be null')
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
                        if not isinstance(fid,(int,str)) or not fid:
                            raise InvestError(2007,msg='finances[\'id\'] must be a int/str type')
                        projAttachment = self.get_object(fid)
                        if request.user.has_perm('proj.admin_changeproj'):
                            pass
                        elif request.user.has_perm('proj.user_changeproj',projAttachment.proj):
                            pass
                        else:
                            raise InvestError(code=2009)
                        f['lastmodifyuser'] = request.user.id
                        f['lastmodifytime'] = datetime.datetime.now()
                        attachmentSer = FinanceChangeSerializer(projAttachment,data=attachmentdata)
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
                    raise InvestError(code=20071,msg='\'finances\' expect an not null list')
                lang = request.GET.get('lang')
                returnlist = []
                for projattachmentid in attachmentidlist:
                    projattachment = self.get_object(projattachmentid)
                    if request.user.has_perm('proj.user_changeproj', projattachment.proj):
                        pass
                    elif request.user.has_perm('proj.admin_changeproj'):
                        pass
                    else:
                        raise InvestError(code=2009, msg='没有权限')
                    projattachment.is_deleted = True
                    projattachment.deleteduser = request.user
                    projattachment.deletedtime = datetime.datetime.now()
                    projattachment.save()
                    deleteqiniufile(projattachment.bucket,projattachment.key)
                    returnlist.append(FinanceSerializer(projattachment).data)
                return JSONResponse(SuccessResponse(returnListChangeToLanguage(returnlist,lang).data))
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
    redis_key = 'projectFinanace'
    Model = finance


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
            obj = read_from_cache(self.redis_key + '_%s' % pk)
            if not obj:
                try:
                    obj = self.queryset.get(id=pk)
                except finance.DoesNotExist:
                    raise InvestError(code=40031)
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
                except finance.DoesNotExist:
                    raise InvestError(code=40031)
                else:
                    write_to_cache(self.redis_key + '_%s' % self.kwargs[lookup_url_kwarg], obj)
        if obj.datasource != self.request.user.datasource:
            raise InvestError(code=8888, msg='资源非同源')
        return obj

    @loginTokenIsAvailable()
    def list(self, request, *args, **kwargs):
        try:
            page_size = request.GET.get('page_size')
            page_index = request.GET.get('page_index')  # 从第一页开始
            lang = request.GET.get('lang')
            if not page_size:
                page_size = 10
            if not page_index:
                page_index = 1
            queryset = self.filter_queryset(self.get_queryset())
            if not request.user.has_perm('proj.admin_getproj'):
                queryset = queryset
            else:
                queryset = queryset.filter(proj__createuser__id=request.user.id)
            try:
                count = queryset.count()
                queryset = Paginator(queryset, page_size)
            except EmptyPage:
                return JSONResponse(SuccessResponse([],msg='没有符合的结果'))
            queryset = queryset.page(page_index)
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
            try:
                proj = project.objects.get(id=projid,is_deleted=False,datasource=request.user.datasource)
            except project.DoesNotExist:
                raise InvestError(code=4002,msg='指定内容不存在')
            if request.user.has_perm('proj.admin_changeproj'):
                pass
            elif request.user.has_perm('proj.user_changeproj',proj):
                pass
            else:
                raise InvestError(code=2009,msg='没有增加该项目财务信息的权限')
            lang = request.GET.get('lang')
            financedata = data.get('finances')
            with transaction.atomic():
                if financedata:
                    for f in financedata:
                        f['proj'] = proj.pk
                        f['createuser'] = request.user.id
                        f['datasource'] = request.user.datasource.id
                    finances = FinanceCreateSerializer(data=financedata,many=True)
                    if finances.is_valid():
                       finances.save()
                    else:
                        raise InvestError(code=4001,msg='财务信息有误_%s\n%s' % (finances.error_messages, finances.errors))
                else:
                    raise InvestError(code=20071,msg='finances field cannot be null')
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
                        if not isinstance(fid,(int,str)) or not fid:
                            raise InvestError(2007,msg='finances[\'id\'] must be a int/str type')
                        projfinance = self.get_object(fid)
                        if request.user.has_perm('proj.admin_changeproj'):
                            pass
                        elif request.user.has_perm('proj.user_changeproj',projfinance.proj):
                            pass
                        else:
                            raise InvestError(code=2009)
                        f['lastmodifyuser'] = request.user.id
                        f['lastmodifytime'] = datetime.datetime.now()
                        finance = FinanceChangeSerializer(projfinance,data=financedata)
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
                    elif request.user.has_perm('proj.admin_changeproj'):
                        pass
                    else:
                        raise InvestError(code=2009, msg='没有权限')
                    projfinance.is_deleted = True
                    projfinance.deleteduser = request.user
                    projfinance.deletedtime = datetime.datetime.now()
                    projfinance.save()
                    returnlist.append(FinanceSerializer(projfinance).data)
                return JSONResponse(SuccessResponse(returnListChangeToLanguage(returnlist,lang).data))
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
    queryset = favoriteProject.objects.all().filter(is_deleted=False)
    filter_fields = ('user','trader','favoritetype')
    serializer_class = FavoriteSerializer
    Model = favoriteProject

    def get_queryset(self,datasource=None):
        assert self.queryset is not None, (
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method."
            % self.__class__.__name__
        )
        queryset = self.queryset
        if isinstance(queryset, QuerySet):
            if datasource:
                queryset = queryset.filter(datasource=datasource)
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
            raise InvestError(code=8888, msg='资源非同源')
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
            raise InvestError(code=8888, msg='资源非同源')
        if obj.is_deleted:
            raise InvestError(code=2002,msg='用户已删除')
        return obj

    #获取收藏列表，GET参数'user'，'trader'，'favoritetype'
    @loginTokenIsAvailable()
    def list(self, request, *args, **kwargs):
        try:
            page_size = request.GET.get('page_size')
            page_index = request.GET.get('page_index')  # 从第一页开始
            lang = request.GET.get('lang')
            userid = request.GET.get('user')
            traderid = request.GET.get('trader')
            ftype = request.GET.get('favoritetype')
            if not ftype or not userid or (ftype == 3 and not traderid):
                raise InvestError(code=20072,msg='favoritetype and user cannot be null')
            if not page_size:
                page_size = 10
            if not page_index:
                page_index = 1
            queryset = self.filter_queryset(self.get_queryset())
            user = self.get_user(userid)
            if request.user == user:
                pass
            elif request.user.has_perm('proj.admin_getfavorite'):
                pass
            elif request.user.has_perm('proj.user_getfavorite',user):
                pass
            else:
                raise InvestError(code=2009)
            try:
                count = queryset.count()
                queryset = Paginator(queryset, page_size)
            except EmptyPage:
                raise InvestError(1001)
            queryset = queryset.page(page_index)
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
            if request.user == user:
                if ftype not in [4,5]:
                    raise InvestError(code=4005)
            elif request.user.has_perm('proj.admin_addfavorite'):
                if ftype not in [1,2]:
                    raise InvestError(code=4005)
            elif request.user.has_perm('proj.user_addfavorite',user):
                if ftype != 3:
                    raise InvestError(code=4005)
            else:
                raise InvestError(code=2009)
            with transaction.atomic():
                favoriteProjectList = []
                for projid in projidlist:
                    data['proj'] = projid
                    newfavorite = FavoriteCreateSerializer(data=data)
                    if newfavorite.is_valid():
                        newfavoriteproj = newfavorite.save()
                        if newfavoriteproj.user.datasource != request.user.datasource or newfavoriteproj.proj.datasource != request.user.datasource or\
                                (newfavoriteproj.trader and newfavoriteproj.trader.datasource != request.user.datasource):
                            raise InvestError(code=8888)
                        favoriteProjectList.append(newfavorite.data)
                    else:
                        raise InvestError(code=20071,msg='%s'%newfavorite.errors)
                    return JSONResponse(SuccessResponse(returnDictChangeToLanguage(newfavorite.data,lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    #批量删除（参数传收藏model的idlist）
    @loginTokenIsAvailable()
    def destroy(self, request, *args, **kwargs):
        try:
            favoridlist = request.data.get('favotiteids')
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
