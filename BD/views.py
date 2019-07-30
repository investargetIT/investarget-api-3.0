#coding=utf8

import traceback
from django.core.paginator import Paginator, EmptyPage
from django.db import transaction
from django.db.models import QuerySet, Q, Count, Max
from django.shortcuts import render_to_response
from django_filters import FilterSet
import datetime
import json
from django.core.serializers.json import DjangoJSONEncoder
from rest_framework import filters, viewsets
from BD.models import ProjectBD, ProjectBDComments, OrgBDComments, OrgBD, MeetingBD, MeetBDShareToken
from BD.serializers import ProjectBDSerializer, ProjectBDCreateSerializer, ProjectBDCommentsCreateSerializer, \
    ProjectBDCommentsSerializer, OrgBDCommentsSerializer, OrgBDCommentsCreateSerializer, OrgBDCreateSerializer, \
    OrgBDSerializer, MeetingBDSerializer, MeetingBDCreateSerializer
from invest.settings import cli_domain
from proj.models import project
from third.views.qiniufile import deleteqiniufile
from timeline.models import timeline
from timeline.models import timelineremark
from utils.customClass import RelationFilter, InvestError, JSONResponse
from utils.sendMessage import sendmessage_orgBDMessage, sendmessage_orgBDExpireMessage
from utils.util import loginTokenIsAvailable, SuccessResponse, InvestErrorResponse, ExceptionResponse, \
    returnListChangeToLanguage, catchexcption, returnDictChangeToLanguage, mySortQuery, add_perm, rem_perm, \
    read_from_cache, write_to_cache, cache_delete_key, logexcption, cache_delete_patternKey, checkSessionToken


class ProjectBDFilter(FilterSet):
    com_name = RelationFilter(filterstr='com_name',lookup_method='icontains')
    location = RelationFilter(filterstr='location', lookup_method='in')
    contractors = RelationFilter(filterstr='contractors', lookup_method='in')
    indGroup = RelationFilter(filterstr='indGroup', lookup_method='in')
    country = RelationFilter(filterstr='country', lookup_method='in')
    username = RelationFilter(filterstr='username', lookup_method='icontains')
    usermobile = RelationFilter(filterstr='usermobile', lookup_method='contains')
    source = RelationFilter(filterstr='source',lookup_method='icontains')
    manager = RelationFilter(filterstr='manager',lookup_method='in')
    bd_status = RelationFilter(filterstr='bd_status', lookup_method='in')
    source_type = RelationFilter(filterstr='source_type', lookup_method='in')
    stime = RelationFilter(filterstr='createdtime', lookup_method='gt')
    etime = RelationFilter(filterstr='createdtime', lookup_method='lt')
    class Meta:
        model = ProjectBD
        fields = ('com_name','location', 'contractors', 'indGroup', 'username','usermobile','source','manager','bd_status','source_type', 'stime', 'etime')


class ProjectBDView(viewsets.ModelViewSet):
    """
    list:获取新项目BD
    create:增加新项目BD
    retrieve:查看新项目BD信息
    update:修改bd信息
    destroy:删除新项目BD
    """
    filter_backends = (filters.DjangoFilterBackend,filters.SearchFilter)
    queryset = ProjectBD.objects.filter(is_deleted=False)
    filter_class = ProjectBDFilter
    search_fields = ('com_name', 'username', 'source')
    serializer_class = ProjectBDSerializer

    def get_queryset(self):
        assert self.queryset is not None, (
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method."
            % self.__class__.__name__
        )
        queryset = self.queryset
        if isinstance(queryset, QuerySet):
            if self.request.user.is_authenticated:
                queryset = queryset.filter(datasource_id=self.request.user.datasource_id)
            else:
                queryset = queryset
        else:
            raise InvestError(code=8890)
        return queryset



    @loginTokenIsAvailable()
    def list(self, request, *args, **kwargs):
        try:
            page_size = request.GET.get('page_size', 10)
            page_index = request.GET.get('page_index', 1)
            lang = request.GET.get('lang', 'cn')
            queryset = self.filter_queryset(self.get_queryset())
            if request.user.has_perm('BD.manageProjectBD') or request.user.has_perm('usersys.as_trader'):
                pass
            elif request.user.has_perm('BD.user_getProjectBD'):
                queryset = queryset.filter(Q(manager=request.user) | Q(contractors=request.user) | Q(createuser=request.user))
            else:
                raise InvestError(2009)
            countres = queryset.values_list('manager').annotate(Count('manager'))
            countlist = []
            for manager_count in countres:
                countlist.append({'manager': manager_count[0], 'count': manager_count[1]})
            sortfield = request.GET.get('sort', 'createdtime')
            desc = request.GET.get('desc', 1)
            queryset = mySortQuery(queryset, sortfield, desc)
            try:
                count = queryset.count()
                queryset = Paginator(queryset, page_size)
                queryset = queryset.page(page_index)
            except EmptyPage:
                return JSONResponse(SuccessResponse({'count': 0, 'data': [], 'manager_count':countlist}))
            serializer = ProjectBDSerializer(queryset, many=True)
            return JSONResponse(SuccessResponse({'count':count,'data':returnListChangeToLanguage(serializer.data,lang),'manager_count':countlist}))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable()
    def countBd(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            if request.user.has_perm('BD.manageProjectBD'):
                pass
            elif request.user.has_perm('BD.user_getProjectBD'):
                pass
            else:
                raise InvestError(2009)
            countres = queryset.values_list('manager').annotate(Count('manager'))
            countlist = []
            for manager_count in countres:
                countlist.append({'manager': manager_count[0], 'count': manager_count[1]})
            count = queryset.count()
            return JSONResponse(SuccessResponse({'count': count, 'manager_count': countlist}))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))


    @loginTokenIsAvailable()
    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            lang = request.GET.get('lang')
            comments = data.get('comments',None)
            data['createuser'] = request.user.id
            data['datasource'] = request.user.datasource.id
            data['manager'] = data['manager'] if data.get('manager') else request.user.id
            data['contractors'] = data['contractors'] if data.get('contractors') else request.user.id
            if request.user.has_perm('BD.manageProjectBD'):
                pass
            elif request.user.has_perm('BD.user_addProjectBD'):
                pass
            else:
                raise InvestError(2009)
            with transaction.atomic():
                projectBD = ProjectBDCreateSerializer(data=data)
                if projectBD.is_valid():
                    newprojectBD = projectBD.save()
                    if newprojectBD.manager:
                        add_perm('BD.user_manageProjectBD', newprojectBD.manager, newprojectBD)
                else:
                    raise InvestError(4009,msg='项目BD创建失败——%s'%projectBD.errors)
                if comments:
                    data['projectBD'] = newprojectBD.id
                    commentinstance = ProjectBDCommentsCreateSerializer(data=data)
                    if commentinstance.is_valid():
                        commentinstance.save()
                return JSONResponse(SuccessResponse(returnDictChangeToLanguage(ProjectBDSerializer(newprojectBD).data,lang)))
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
            if request.user.has_perm('BD.manageProjectBD'):
                pass
            elif request.user in [instance.manager, instance.contractors, instance.createuser]:
                pass
            else:
                raise InvestError(2009)
            serializer = self.serializer_class(instance)
            return JSONResponse(SuccessResponse(returnDictChangeToLanguage(serializer.data, lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable()
    def update(self, request, *args, **kwargs):
        try:
            data = request.data
            lang = request.GET.get('lang')
            instance = self.get_object()
            data.pop('createuser', None)
            data.pop('datasource', None)
            if request.user.has_perm('BD.manageProjectBD'):
                pass
            elif request.user in [instance.manager, instance.contractors, instance.createuser]:
                pass
            else:
                raise InvestError(2009)
            with transaction.atomic():
                projectBD = ProjectBDCreateSerializer(instance,data=data)
                if projectBD.is_valid():
                    newprojectBD = projectBD.save()
                else:
                    raise InvestError(4009, msg='项目BD修改失败——%s' % projectBD.errors)
                return JSONResponse(
                    SuccessResponse(returnDictChangeToLanguage(ProjectBDSerializer(newprojectBD).data, lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))


    @loginTokenIsAvailable()
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            if request.user.has_perm('BD.manageProjectBD'):
                pass
            elif request.user in [instance.manager, instance.contractors, instance.createuser]:
                pass
            else:
                raise InvestError(2009)
            with transaction.atomic():
                instance.is_deleted = True
                instance.deleteduser = request.user
                instance.deletedtime = datetime.datetime.now()
                instance.save()
                instance.ProjectBD_comments.filter(is_deleted=False).update(is_deleted=True, deleteduser=request.user, deletedtime=datetime.datetime.now())
            return JSONResponse(SuccessResponse({'isDeleted': True,}))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))


class ProjectBDCommentsView(viewsets.ModelViewSet):
    """
    list:获取新项目BDcomments
    create:增加新项目BDcomments
    destroy:删除新项目BDcomments
    """
    filter_backends = (filters.DjangoFilterBackend,)
    queryset = ProjectBDComments.objects.filter(is_deleted=False)
    filter_fields = ('projectBD',)
    serializer_class = ProjectBDCommentsSerializer

    def get_queryset(self):
        assert self.queryset is not None, (
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method."
            % self.__class__.__name__
        )
        queryset = self.queryset
        if isinstance(queryset, QuerySet):
            if self.request.user.is_authenticated:
                queryset = queryset.filter(datasource_id=self.request.user.datasource_id)
            else:
                queryset = queryset
        else:
            raise InvestError(code=8890)
        return queryset

    @loginTokenIsAvailable()
    def list(self, request, *args, **kwargs):
        try:
            page_size = request.GET.get('page_size', 10)
            page_index = request.GET.get('page_index', 1)
            lang = request.GET.get('lang', 'cn')
            queryset = self.filter_queryset(self.get_queryset())
            if request.user.has_perm('BD.manageProjectBD'):
                pass
            elif request.user.has_perm('BD.user_getProjectBD'):
                queryset = queryset.filter(projectBD__in=request.user.user_projBDs.all())
            else:
                raise InvestError(2009)
            queryset = queryset.order_by('-createdtime')
            try:
                count = queryset.count()
                queryset = Paginator(queryset, page_size)
                queryset = queryset.page(page_index)
            except EmptyPage:
                return JSONResponse(SuccessResponse({'count': 0, 'data': []}))
            serializer = ProjectBDCommentsSerializer(queryset, many=True)
            return JSONResponse(
                SuccessResponse({'count': count, 'data': returnListChangeToLanguage(serializer.data, lang)}))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable()
    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            bdinstance = ProjectBD.objects.get(id=int(data['projectBD']))
            if request.user.has_perm('BD.manageProjectBD'):
                pass
            elif request.user in [bdinstance.manager, bdinstance.contractors, bdinstance.createuser]:
                pass
            else:
                raise InvestError(2009)
            lang = request.GET.get('lang')
            data['createuser'] = request.user.id
            data['datasource'] = request.user.datasource.id
            with transaction.atomic():
                commentinstance = ProjectBDCommentsCreateSerializer(data=data)
                if commentinstance.is_valid():
                    newcommentinstance = commentinstance.save()
                else:
                    raise InvestError(4009, msg='创建项目BDcomments失败--%s' % commentinstance.error_messages)
                return JSONResponse(SuccessResponse(returnDictChangeToLanguage(ProjectBDCommentsSerializer(newcommentinstance).data, lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable()
    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            if request.user.has_perm('BD.manageProjectBD'):
                pass
            elif request.user.id == instance.createuser_id:
                pass
            else:
                raise InvestError(2009)
            lang = request.GET.get('lang')
            data = request.data
            with transaction.atomic():
                commentinstance = ProjectBDCommentsCreateSerializer(instance, data=data)
                if commentinstance.is_valid():
                    newcommentinstance = commentinstance.save()
                else:
                    raise InvestError(4009, msg='修改项目BDcomments失败--%s' % commentinstance.error_messages)
                return JSONResponse(SuccessResponse(
                    returnDictChangeToLanguage(ProjectBDCommentsSerializer(newcommentinstance).data, lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))



    @loginTokenIsAvailable()
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            if request.user.has_perm('BD.manageProjectBD'):
                pass
            elif request.user.id == instance.createuser_id:
                pass
            else:
                raise InvestError(2009)
            with transaction.atomic():
                instance.is_deleted = True
                instance.deleteduser = request.user
                instance.deletedtime = datetime.datetime.now()
                instance.save()
            return JSONResponse(SuccessResponse({'isDeleted': True, }))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))


class OrgBDFilter(FilterSet):
    manager = RelationFilter(filterstr='manager',lookup_method='in')
    org = RelationFilter(filterstr='org', lookup_method='in')
    response = RelationFilter(filterstr='response', lookup_method='in')
    proj = RelationFilter(filterstr='proj', lookup_method='in')
    isSolved = RelationFilter(filterstr='isSolved')
    isRead = RelationFilter(filterstr='isRead')
    isimportant = RelationFilter(filterstr='isimportant')
    stime = RelationFilter(filterstr='createdtime', lookup_method='gt')
    etime = RelationFilter(filterstr='createdtime', lookup_method='lt')
    class Meta:
        model = OrgBD
        fields = ('manager', 'org', 'proj', 'stime', 'etime', 'response', 'isimportant', 'isSolved', 'isRead')


class OrgBDView(viewsets.ModelViewSet):
    """
    countBDProjectOrg:统计机构BD项目机构
    countBDManager:统计机构BD负责人
    countBDProject:统计机构BD项目
    countBDResponse:统计机构BD状态
    list:获取机构BD
    create:增加机构BD
    retrieve:查看机构BD信息
    readBd:已读回执
    update:修改机构BD信息
    destroy:删除机构BD
    """
    filter_backends = (filters.DjangoFilterBackend,filters.SearchFilter)
    queryset = OrgBD.objects.filter(is_deleted=False)
    filter_class = OrgBDFilter
    search_fields = ('proj__projtitleC', 'username', 'usermobile', 'manager__usernameC', 'org__orgnameC', 'org__orgnameE')
    serializer_class = OrgBDSerializer
    redis_key = 'org_bd'

    def get_queryset(self):
        assert self.queryset is not None, (
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method."
            % self.__class__.__name__
        )
        queryset = read_from_cache(self.redis_key)
        if not queryset:
            queryset = self.queryset
            write_to_cache(self.redis_key, queryset)
        if isinstance(queryset, QuerySet):
            if self.request.user.is_authenticated:
                queryset = queryset.filter(datasource_id=self.request.user.datasource_id)
            else:
                queryset = queryset
        else:
            raise InvestError(code=8890)
        return queryset

    @loginTokenIsAvailable()
    def countBDProjectOrg(self, request, *args, **kwargs):
        try:
            page_size = request.GET.get('page_size', 10)
            page_index = request.GET.get('page_index', 1)
            if request.user.has_perm('BD.manageOrgBD') or request.user.has_perm('BD.user_getOrgBD'):
                pass
            else:
                raise InvestError(2009)
            queryset = self.filter_queryset(self.get_queryset())
            sortfield = request.GET.get('sort', 'created')
            if request.GET.get('desc', 1) in ('1', u'1', 1):
                sortfield = '-' + sortfield
            queryset = queryset.values('org','proj').annotate(orgcount=Count('org'),projcount=Count('proj'),created=Max('createdtime')).order_by(sortfield)
            try:
                count = queryset.count()
                queryset = Paginator(queryset, page_size)
                queryset = queryset.page(page_index)
            except EmptyPage:
                return JSONResponse(SuccessResponse({'count': 0, 'data': []}))
            serializer = json.dumps(list(queryset), cls=DjangoJSONEncoder)
            return JSONResponse(SuccessResponse({'count': count, 'data': json.loads(serializer)}))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable()
    def countBDProject(self, request, *args, **kwargs):
        try:
            if request.user.has_perm('BD.manageOrgBD') or request.user.has_perm('BD.user_getOrgBD'):
                pass
            else:
                raise InvestError(2009)
            page_size = request.GET.get('page_size', 10)
            page_index = request.GET.get('page_index', 1)
            queryset = self.filter_queryset(self.get_queryset())
            sortfield = request.GET.get('sort', 'created')
            if request.GET.get('desc', 1) in ('1', u'1', 1):
                sortfield = '-' + sortfield
            queryset = queryset.values('proj').annotate(count=Count('proj'), created=Max('createdtime')).order_by(sortfield)
            try:
                count = queryset.count()
                queryset = Paginator(queryset, page_size)
                queryset = queryset.page(page_index)
            except EmptyPage:
                return JSONResponse(SuccessResponse({'count': 0, 'data': []}))
            serializer = json.dumps(list(queryset), cls=DjangoJSONEncoder)
            return JSONResponse(SuccessResponse({'count': count, 'data': json.loads(serializer)}))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))


    @loginTokenIsAvailable()
    def list(self, request, *args, **kwargs):
        try:
            if request.user.has_perm('BD.manageOrgBD') or request.user.has_perm('BD.user_getOrgBD'):
                pass
            else:
                raise InvestError(2009)
            query_string = request.META['QUERY_STRING']
            uriPath = str(request.path)
            cachekey = '{}_{}_{}'.format(uriPath, query_string, request.user.id)
            response = read_from_cache(cachekey)
            if response:
                return JSONResponse(SuccessResponse(response))
            page_size = request.GET.get('page_size', 10)
            page_index = request.GET.get('page_index', 1)
            lang = request.GET.get('lang', 'cn')
            queryset = self.filter_queryset(self.get_queryset())
            sortfield = request.GET.get('sort', 'createdtime')
            desc = request.GET.get('desc', 1)
            if desc in ('1', u'1', 1):
                sortfield = '-' + sortfield
            queryset = queryset.order_by(sortfield)
            try:
                count = queryset.count()
                queryset = Paginator(queryset, page_size)
                queryset = queryset.page(page_index)
            except EmptyPage:
                return JSONResponse(SuccessResponse({'count': 0, 'data': []}))
            serializer = OrgBDSerializer(queryset, many=True, context={'user_id': request.user.id})
            response = {'count':count,'data':returnListChangeToLanguage(serializer.data,lang)}
            write_to_cache(cachekey, response)
            return JSONResponse(SuccessResponse(response))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable()
    def countBDManager(self, request, *args, **kwargs):
        try:
            if request.user.has_perm('BD.manageOrgBD'):
                pass
            elif request.user.has_perm('BD.user_getOrgBD'):
                pass
            else:
                raise InvestError(2009)
            queryset = self.filter_queryset(self.get_queryset())
            count = queryset.count()
            queryset = queryset.values_list('manager').annotate(count=Count('manager'))
            serializer = json.dumps(list(queryset), cls=DjangoJSONEncoder)
            return JSONResponse(SuccessResponse({'count': count, 'manager_count': json.loads(serializer)}))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable()
    def countBDResponse(self, request, *args, **kwargs):
        try:
            if request.user.has_perm('BD.manageOrgBD'):
                pass
            elif request.user.has_perm('BD.user_getOrgBD'):
                pass
            else:
                raise InvestError(2009)
            queryset = self.filter_queryset(self.get_queryset())
            count = queryset.count()
            queryset = queryset.values('response').annotate(count=Count('*'))
            serializer = json.dumps(list(queryset), cls=DjangoJSONEncoder)
            return JSONResponse(SuccessResponse({'count': count, 'response_count': json.loads(serializer)}))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable()
    def create(self, request, *args, **kwargs):
        try:
            checkSessionToken(request)
            data = request.data
            lang = request.GET.get('lang')
            comments = data.get('comments',None)
            data['createuser'] = request.user.id
            data['datasource'] = request.user.datasource.id
            if request.user.has_perm('BD.manageOrgBD'):
                pass
            else:
                proj = data.get('proj', None)
                if proj:
                    projinstance = project.objects.get(id=proj, is_deleted=False, datasource=request.user.datasource)
                    if request.user.has_perm('BD.user_addOrgBD'):
                        pass
                    elif request.user in [projinstance.takeUser, projinstance.makeUser]:
                        pass
                    else:
                        raise InvestError(2009)
                else:
                    raise InvestError(2009)
            with transaction.atomic():
                orgBD = OrgBDCreateSerializer(data=data)
                if orgBD.is_valid():
                    neworgBD = orgBD.save()
                    if neworgBD.manager:
                        if request.user != neworgBD.manager:
                            today = datetime.date.today()
                            if len(self.queryset.filter(createdtime__year=today.year, createdtime__month=today.month,
                                                        createdtime__day=today.day, manager_id=neworgBD.manager, proj=neworgBD.proj)) == 1:
                                sendmessage_orgBDMessage(neworgBD, receiver=neworgBD.manager,
                                                         types=['app', 'webmsg', 'sms'], sender=request.user)
                        add_perm('BD.user_manageOrgBD', neworgBD.manager, neworgBD)
                else:
                    raise InvestError(5004,msg='机构BD创建失败——%s'%orgBD.error_messages)
                if comments:
                    data['orgBD'] = neworgBD.id
                    commentinstance = OrgBDCommentsCreateSerializer(data=data)
                    if commentinstance.is_valid():
                        commentinstance.save()
                cache_delete_key(self.redis_key)
                cache_delete_patternKey(key='/bd/orgbd*')
                return JSONResponse(SuccessResponse(returnDictChangeToLanguage(OrgBDSerializer(neworgBD, context={'user_id': request.user.id}).data,lang)))
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
            if request.user.has_perm('BD.manageOrgBD'):
                pass
            elif request.user.has_perm('BD.user_manageOrgBD', instance):
                pass
            else:
                raise InvestError(2009)
            serializer = self.serializer_class(instance, context={'user_id': request.user.id})
            return JSONResponse(SuccessResponse(returnDictChangeToLanguage(serializer.data, lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable()
    def readBd(self, request, *args, **kwargs):
        try:
            data = request.data
            bdlist = data.get('bds')
            bdQuery = self.get_queryset().filter(manager_id=request.user.id, id__in=bdlist)
            count = 0
            if bdQuery.exists():
                count = bdQuery.count()
                bdQuery.update(isRead=True)
                cache_delete_patternKey(key='/bd/orgbd*')
            return JSONResponse(SuccessResponse({'count': count}))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable()
    def update(self, request, *args, **kwargs):
        try:
            data = request.data
            data['lastmodifyuser'] = request.user.id
            lang = request.GET.get('lang')
            instance = self.get_object()
            oldmanager = instance.manager
            data.pop('createuser', None)
            data.pop('datasource', None)
            remark = data.get('remark', None)
            if request.user.has_perm('BD.manageOrgBD'):
                pass
            elif request.user.id == instance.createuser_id:
                data = {'response': data.get('response', instance.response_id),
                        'isimportant': bool(data.get('isimportant', instance.isimportant)),
                        'lastmodifyuser': request.user.id}

            elif request.user.has_perm('BD.user_manageOrgBD', instance):
                data = {'response': data.get('response', instance.response_id),
                        'isimportant': bool(data.get('isimportant', instance.isimportant)),
                        'lastmodifyuser': request.user.id}
            elif instance.proj:
                if request.user in [instance.proj.takeUser, instance.proj.makeUser]:
                    data = {'response': data.get('response', instance.response_id),
                            'isimportant': bool(data.get('isimportant', instance.isimportant)),
                            'lastmodifyuser': request.user.id}
            else:
                raise InvestError(2009)
            with transaction.atomic():
                orgBD = OrgBDCreateSerializer(instance,data=data)
                if orgBD.is_valid():
                    neworgBD = orgBD.save()
                    cache_delete_patternKey(key='/bd/orgbd*')
                    if remark and remark.strip() != '' and neworgBD.response_id not in [4, 5, 6, None] and neworgBD.bduser and neworgBD.proj:
                        try:
                            timeline_qs = timeline.objects.filter(is_deleted=0, investor=neworgBD.bduser,
                                                                  proj=neworgBD.proj, trader=neworgBD.manager)
                            if timeline_qs.exists():
                                timelineremark(timeline=timeline_qs.first(), remark=remark,
                                               createuser=neworgBD.createuser, datasource=neworgBD.datasource).save()
                        except Exception:
                            logexcption(msg='同步备注失败，OrgBD_id-%s ' % neworgBD.id)
                    oldmanager_id = data.get('manager', None)
                    if oldmanager_id and oldmanager_id != oldmanager.id:
                        if request.user != neworgBD.manager:
                            today = datetime.date.today()
                            if len(self.queryset.filter(createdtime__year=today.year, createdtime__month=today.month,
                                                        createdtime__day=today.day, manager_id=neworgBD.manager, proj=neworgBD.proj)) == 1:
                                sendmessage_orgBDMessage(neworgBD, receiver=neworgBD.manager,
                                                         types=['app', 'webmsg', 'sms'], sender=request.user)
                        add_perm('BD.user_manageOrgBD', neworgBD.manager, neworgBD)
                        rem_perm('BD.user_manageOrgBD', oldmanager, neworgBD)
                else:
                    raise InvestError(5004, msg='机构BD修改失败——%s' % orgBD.error_messages)
                cache_delete_key(self.redis_key)
                return JSONResponse(
                    SuccessResponse(returnDictChangeToLanguage(OrgBDSerializer(neworgBD, context={'user_id': request.user.id}).data, lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))


    @loginTokenIsAvailable()
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            if request.user.has_perm('BD.manageOrgBD'):
                pass
            elif request.user.id == instance.createuser_id:
                pass
            else:
                raise InvestError(2009)
            with transaction.atomic():
                instance.is_deleted = True
                instance.deleteduser = request.user
                instance.deletedtime = datetime.datetime.now()
                instance.save()
                instance.OrgBD_comments.filter(is_deleted=False).update(is_deleted=True, deleteduser=request.user,
                                                                        deletedtime=datetime.datetime.now())
            cache_delete_key(self.redis_key)
            cache_delete_patternKey(key='/bd/orgbd*')
            return JSONResponse(SuccessResponse({'isDeleted': True,}))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))


class OrgBDCommentsView(viewsets.ModelViewSet):
    """
    list:获取机构BDcomments
    create:增加机构BDcomments
    destroy:删除机构BDcomments
    """
    filter_backends = (filters.DjangoFilterBackend,)
    queryset = OrgBDComments.objects.filter(is_deleted=False)
    filter_fields = ('orgBD',)
    serializer_class = OrgBDCommentsSerializer

    def get_queryset(self):
        assert self.queryset is not None, (
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method."
            % self.__class__.__name__
        )
        queryset = self.queryset
        if isinstance(queryset, QuerySet):
            if self.request.user.is_authenticated:
                queryset = queryset.filter(datasource_id=self.request.user.datasource_id)
            else:
                queryset = queryset
        else:
            raise InvestError(code=8890)
        return queryset



    @loginTokenIsAvailable()
    def list(self, request, *args, **kwargs):
        try:
            page_size = request.GET.get('page_size', 10)
            page_index = request.GET.get('page_index', 1)
            lang = request.GET.get('lang', 'cn')
            queryset = self.filter_queryset(self.get_queryset())
            if request.user.has_perm('BD.manageOrgBD'):
                pass
            elif request.user.has_perm('BD.user_getOrgBD'):
                queryset = queryset.filter(Q(orgBD__createuser=request.user) | Q(orgBD__in=request.user.user_orgBDs.all()) | Q(orgBD__proj__in=request.user.usertake_projs.all()) | Q(orgBD__proj__in=request.user.usermake_projs.all()))
            else:
                raise InvestError(2009)
            try:
                count = queryset.count()
                queryset = Paginator(queryset, page_size)
                queryset = queryset.page(page_index)
            except EmptyPage:
                return JSONResponse(SuccessResponse({'count': 0, 'data': []}))
            serializer = OrgBDCommentsSerializer(queryset, many=True)
            return JSONResponse(
                SuccessResponse({'count': count, 'data': returnListChangeToLanguage(serializer.data, lang)}))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))


    @loginTokenIsAvailable()
    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            bdinstance = OrgBD.objects.get(id=int(data['orgBD']))
            if request.user.has_perm('BD.manageOrgBD'):
                pass
            elif request.user.id == bdinstance.createuser_id:
                pass
            elif request.user.has_perm('BD.user_manageOrgBD', bdinstance):
                pass
            elif bdinstance.proj:
                if request.user in [bdinstance.proj.takeUser, bdinstance.proj.makeUser]:
                    pass
            else:
                raise InvestError(2009)
            lang = request.GET.get('lang')
            data['createuser'] = request.user.id
            data['datasource'] = request.user.datasource.id
            with transaction.atomic():
                commentinstance = OrgBDCommentsCreateSerializer(data=data)
                if commentinstance.is_valid():
                    newcommentinstance = commentinstance.save()
                    cache_delete_patternKey(key='/bd/orgbd*')
                else:
                    raise InvestError(5004, msg='创建机构BDcomments失败--%s' % commentinstance.error_messages)
                return JSONResponse(SuccessResponse(returnDictChangeToLanguage(OrgBDCommentsSerializer(newcommentinstance).data, lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))


    @loginTokenIsAvailable()
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            if request.user.has_perm('BD.manageOrgBD'):
                pass
            elif request.user.id == instance.createuser_id:
                pass
            else:
                raise InvestError(2009)
            with transaction.atomic():
                instance.is_deleted = True
                instance.deleteduser = request.user
                instance.deletedtime = datetime.datetime.now()
                instance.save()
                cache_delete_patternKey(key='/bd/orgbd*')
            return JSONResponse(SuccessResponse({'isDeleted': True, }))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

class MeetBDFilter(FilterSet):
    username = RelationFilter(filterstr='username', lookup_method='icontains')
    usermobile = RelationFilter(filterstr='usermobile', lookup_method='contains')
    manager = RelationFilter(filterstr='manager',lookup_method='in')
    class Meta:
        model = MeetingBD
        fields = ('username','usermobile','manager')


class MeetingBDView(viewsets.ModelViewSet):
    """
    list:获取会议BD
    create:增加会议BD
    retrieve:查看会议BD信息
    update:修改会议BD信息
    destroy:删除会议BD
    getShareMeetingBDdetail:根据sharetoken获取会议BD
    getShareMeetingBDtoken:获取会议BD分享sharetoken
    """
    filter_backends = (filters.DjangoFilterBackend,filters.SearchFilter)
    queryset = MeetingBD.objects.filter(is_deleted=False)
    filter_class = MeetBDFilter
    search_fields = ('proj__projtitleC', 'username','manager__usernameC')
    serializer_class = MeetingBDSerializer

    def get_queryset(self):
        assert self.queryset is not None, (
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method."
            % self.__class__.__name__
        )
        queryset = self.queryset
        if isinstance(queryset, QuerySet):
            if self.request.user.is_authenticated:
                queryset = queryset.filter(datasource_id=self.request.user.datasource_id)
            else:
                queryset = queryset
        else:
            raise InvestError(code=8890)
        return queryset


    @loginTokenIsAvailable()
    def list(self, request, *args, **kwargs):
        try:
            page_size = request.GET.get('page_size', 10)
            page_index = request.GET.get('page_index', 1)
            lang = request.GET.get('lang', 'cn')
            queryset = self.filter_queryset(self.get_queryset())
            if request.user.has_perm('BD.manageMeetBD'):
                pass
            elif request.user.has_perm('BD.user_getMeetBD'):
                queryset = queryset.filter(Q(manager=request.user) | Q(createuser=request.user) | Q(proj__in=request.user.usertake_projs.all()) | Q(proj__in=request.user.usermake_projs.all()))
            else:
                raise InvestError(2009)
            sortfield = request.GET.get('sort', 'createdtime')
            desc = request.GET.get('desc', 1)
            queryset = mySortQuery(queryset, sortfield, desc)
            try:
                count = queryset.count()
                queryset = Paginator(queryset, page_size)
                queryset = queryset.page(page_index)
            except EmptyPage:
                return JSONResponse(SuccessResponse({'count': 0, 'data': []}))
            serializer = MeetingBDSerializer(queryset, many=True)
            return JSONResponse(SuccessResponse({'count':count,'data':returnListChangeToLanguage(serializer.data,lang)}))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))


    @loginTokenIsAvailable()
    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            lang = request.GET.get('lang')
            data['createuser'] = request.user.id
            data['datasource'] = request.user.datasource.id
            if request.user.has_perm('BD.manageMeetBD'):
                pass
            else:
                proj = data.get('proj', None)
                if proj:
                    projinstance = project.objects.get(id=proj, is_deleted=False, datasource=request.user.datasource)
                    if request.user.has_perm('BD.user_addMeetBD'):
                        pass
                    elif request.user in [projinstance.takeUser, projinstance.makeUser]:
                        pass
                    else:
                        raise InvestError(2009)
                else:
                    raise InvestError(2009)
            with transaction.atomic():
                meetBD = MeetingBDCreateSerializer(data=data)
                if meetBD.is_valid():
                    newMeetBD = meetBD.save()
                    if newMeetBD.manager:
                        add_perm('BD.user_manageMeetBD', newMeetBD.manager, newMeetBD)
                else:
                    raise InvestError(5005,msg='会议BD创建失败——%s'%meetBD.error_messages)
                return JSONResponse(SuccessResponse(returnDictChangeToLanguage(MeetingBDSerializer(newMeetBD).data,lang)))
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
            if request.user.has_perm('BD.manageMeetBD'):
                pass
            elif request.user.has_perm('BD.user_manageMeetBD', instance):
                pass
            elif request.user.has_perm('BD.user_getMeetBD'):
                if request.user not in [instance.proj.takeUser, instance.proj.makeUser]:
                    raise InvestError(2009)
            else:
                raise InvestError(2009)
            serializer = self.serializer_class(instance)
            return JSONResponse(SuccessResponse(returnDictChangeToLanguage(serializer.data, lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable()
    def update(self, request, *args, **kwargs):
        try:
            data = request.data
            data.pop('createuser', None)
            data.pop('datasource', None)
            lang = request.GET.get('lang')
            instance = self.get_object()
            oldmanager = instance.manager
            if request.user.has_perm('BD.manageMeetBD'):
                pass
            elif request.user.has_perm('BD.user_manageMeetBD', instance):
                # data = {'comments': data.get('comments', instance.comments),
                #         'attachment': data.get('attachment', instance.attachment),
                #         'attachmentbucket': data.get('attachmentbucket', instance.attachmentbucket),}
                pass
            elif request.user in [instance.proj.takeUser, instance.proj.makeUser]:
                pass
            else:
                raise InvestError(2009)
            with transaction.atomic():
                meetBD = MeetingBDCreateSerializer(instance,data=data)
                if meetBD.is_valid():
                    newMeetBD = meetBD.save()
                    oldmanager_id = data.get('manager', None)
                    if oldmanager_id and oldmanager_id != oldmanager.id:
                        add_perm('BD.user_manageMeetBD', newMeetBD.manager, newMeetBD)
                        rem_perm('BD.user_manageMeetBD', oldmanager, newMeetBD)
                else:
                    raise InvestError(5005, msg='会议BD修改失败——%s' % meetBD.error_messages)
                return JSONResponse(
                    SuccessResponse(returnDictChangeToLanguage(MeetingBDSerializer(newMeetBD).data, lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable()
    def deleteAttachment(self, request, *args, **kwargs):
        try:
            lang = request.GET.get('lang')
            instance = self.get_object()
            if request.user.has_perm('BD.manageMeetBD'):
                pass
            elif request.user.has_perm('BD.user_manageMeetBD', instance):
                pass
            elif request.user in [instance.proj.takeUser, instance.proj.makeUser]:
                pass
            else:
                raise InvestError(2009)
            with transaction.atomic():
                bucket = instance.attachmentbucket
                key = instance.attachment
                deleteqiniufile(bucket, key)
                instance.attachmentbucket = None
                instance.attachment = None
                instance.save()
                return JSONResponse(
                    SuccessResponse(returnDictChangeToLanguage(MeetingBDSerializer(instance).data, lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable(['BD.manageMeetBD',])
    def destroy(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                instance = self.get_object()
                bucket = instance.attachmentbucket
                key = instance.attachment
                deleteqiniufile(bucket, key)
                instance.is_deleted = True
                instance.deleteduser = request.user
                instance.deletedtime = datetime.datetime.now()
                instance.save()
            return JSONResponse(SuccessResponse({'isDeleted': True,}))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))


    @loginTokenIsAvailable()
    def getShareMeetingBDtoken(self, request, *args, **kwargs):
        try:
            data = request.data
            meetinglist = data.get('meetings', None)
            if not isinstance(meetinglist, (list, tuple)):
                raise InvestError(2007, msg='except string list')
            meetings = ','.join(map(str, meetinglist))
            with transaction.atomic():
                sharetokenset = MeetBDShareToken.objects.filter(user=request.user, meetings=meetings)
                if sharetokenset.exists():
                    sharetoken = sharetokenset.last()
                else:
                    sharetoken = MeetBDShareToken(user=request.user, meetings=meetings)
                    sharetoken.save()
                return JSONResponse(SuccessResponse(sharetoken.key))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    def getShareMeetingBDdetail(self, request, *args, **kwargs):
        try:
            lang = request.GET.get('lang')
            tokenkey = request.GET.get('token')
            if tokenkey:
                token = MeetBDShareToken.objects.filter(key=tokenkey)
                if token.exists():
                    meetingstr = token.first().meetings
                    meetinglist = meetingstr.split(',')
                else:
                    raise InvestError(2009,msg='token无效')
            else:
                raise InvestError(2009, msg='token无效')
            serializer = MeetingBDSerializer(self.get_queryset().filter(id__in=meetinglist).order_by('-meet_date'), many=True)
            return JSONResponse(SuccessResponse(returnListChangeToLanguage(serializer.data,lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))



def sendExpiredOrgBDEmail():
    expireday = datetime.date.today() + datetime.timedelta(days=2)
    expiretime_start = datetime.datetime.strptime(str(expireday), '%Y-%m-%d')
    expiretime_end = expiretime_start + datetime.timedelta(days=1)
    orgBD_qs = OrgBD.objects.all().filter(is_deleted=False, isSolved=False,
                                          expirationtime__lt=expiretime_end, expirationtime__gte=expiretime_start)
    managers = orgBD_qs.values_list('manager').annotate(Count('manager'))
    for manager in managers:
        manager_id = manager[0]
        managerbd_qs = orgBD_qs.filter(manager_id=manager_id)
        receiver = managerbd_qs.first().manager
        projs = managerbd_qs.values_list('proj').annotate(Count('proj')).order_by('-proj')
        projlist = []
        for proj in projs:
            projorglist = []
            proj_id = proj[0]
            managerprojbd_qs = managerbd_qs.filter(proj_id=proj_id)
            orgs = managerprojbd_qs.values_list('org').annotate(Count('org'))
            for org in orgs:
                org_id = org[0]
                managerprojorgbd_qs = managerprojbd_qs.filter(org_id=org_id)
                projorgtask = OrgBDSerializer(managerprojorgbd_qs, many=True).data
                if len(projorgtask) > 0:
                    projorgtask[0]['orgspan'] = len(projorgtask)
                projorglist.extend(projorgtask)
            if len(projorglist) > 0:
                projorglist[0]['projspan'] = len(projorglist)
            projlist.extend(projorglist)
        aaa = {'orgbd_qs': projlist, 'cli_domain' : cli_domain}
        html = render_to_response('OrgBDMail_template_cn.html', aaa).content
        sendmessage_orgBDExpireMessage(receiver, ['email'], html)
