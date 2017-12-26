#coding=utf8
import traceback

from django.core.paginator import Paginator, EmptyPage
from django.db import transaction
from django.db.models import Q, Count
from django.db.models import QuerySet
from django_filters import FilterSet
import datetime
# Create your views here.
from rest_framework import filters, viewsets
from BD.models import ProjectBD, ProjectBDComments, OrgBDComments, OrgBD, MeetingBD
from BD.serializers import ProjectBDSerializer, ProjectBDCreateSerializer, ProjectBDCommentsCreateSerializer, \
    ProjectBDCommentsSerializer, OrgBDCommentsSerializer, OrgBDCommentsCreateSerializer, OrgBDCreateSerializer, \
    OrgBDSerializer, MeetingBDSerializer, MeetingBDCreateSerializer
from proj.models import project
from utils.customClass import RelationFilter, InvestError, JSONResponse
from utils.sendMessage import sendmessage_orgBDMessage
from utils.util import loginTokenIsAvailable, SuccessResponse, InvestErrorResponse, ExceptionResponse, \
    returnListChangeToLanguage, catchexcption, returnDictChangeToLanguage, mySortQuery, add_perm, rem_perm


class ProjectBDFilter(FilterSet):
    com_name = RelationFilter(filterstr='com_name',lookup_method='icontains')
    location = RelationFilter(filterstr='location', lookup_method='in')
    username = RelationFilter(filterstr='username', lookup_method='icontains')
    usermobile = RelationFilter(filterstr='usermobile', lookup_method='contains')
    source = RelationFilter(filterstr='source',lookup_method='icontains')
    manager = RelationFilter(filterstr='manager',lookup_method='in')
    bd_status = RelationFilter(filterstr='bd_status', lookup_method='in')
    source_type = RelationFilter(filterstr='source_type', lookup_method='in')
    class Meta:
        model = ProjectBD
        fields = ('com_name','location','username','usermobile','source','manager','bd_status','source_type')


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
                queryset = queryset.filter(datasource=self.request.user.datasource_id)
            else:
                queryset = queryset
        else:
            raise InvestError(code=8890)
        return queryset



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
            if request.user.has_perm('BD.manageProjectBD'):
                pass
            elif request.user.has_perm('BD.user_getProjectBD'):
                queryset = queryset.filter(manager=request.user)
            else:
                raise InvestError(2009)
            sortfield = request.GET.get('sort', 'createdtime')
            desc = request.GET.get('desc', 1)
            queryset = mySortQuery(queryset, sortfield, desc)
            countres = queryset.values_list('manager').annotate(Count('manager'))
            countlist = []
            for manager_count in countres:
                countlist.append({'manager': manager_count[0], 'count': manager_count[1]})
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
    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            lang = request.GET.get('lang')
            comments = data.get('comments',None)
            data['createuser'] = request.user.id
            data['datasource'] = request.user.datasource.id
            if request.user.has_perm('BD.manageProjectBD'):
                pass
            elif request.user.has_perm('BD.user_addProjectBD'):
                data['manager'] = request.user.id
            else:
                raise InvestError(2009)
            with transaction.atomic():
                projectBD = ProjectBDCreateSerializer(data=data)
                if projectBD.is_valid():
                    newprojectBD = projectBD.save()
                    if newprojectBD.manager:
                        add_perm('BD.user_manageProjectBD', newprojectBD.manager, newprojectBD)
                else:
                    raise InvestError(4009,msg='项目BD创建失败——%s'%projectBD.error_messages)
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
            elif request.user.has_perm('BD.user_manageProjectBD', instance):
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
            oldmanager = instance.manager
            data.pop('createuser', None)
            data.pop('datasource', None)
            if request.user.has_perm('BD.manageProjectBD'):
                pass
            elif request.user.has_perm('BD.user_manageProjectBD', instance):
                data = {'bd_status': data.get('bd_status', instance.bd_status_id)}
            else:
                raise InvestError(2009)
            with transaction.atomic():
                projectBD = ProjectBDCreateSerializer(instance,data=data)
                if projectBD.is_valid():
                    newprojectBD = projectBD.save()
                    oldmanager_id = data.get('manager', None)
                    if oldmanager_id and oldmanager_id != oldmanager.id:
                        add_perm('BD.user_manageProjectBD', newprojectBD.manager, newprojectBD)
                        rem_perm('BD.user_manageProjectBD', oldmanager, newprojectBD)
                else:
                    raise InvestError(4009, msg='项目BD修改失败——%s' % projectBD.error_messages)
                return JSONResponse(
                    SuccessResponse(returnDictChangeToLanguage(ProjectBDSerializer(newprojectBD).data, lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))


    @loginTokenIsAvailable(['BD.manageProjectBD',])
    def destroy(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                instance = self.get_object()
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
                queryset = queryset.filter(datasource=self.request.user.datasource_id)
            else:
                queryset = queryset
        else:
            raise InvestError(code=8890)
        return queryset

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
            if request.user.has_perm('BD.manageProjectBD'):
                pass
            elif request.user.has_perm('BD.user_getProjectBD'):
                queryset = queryset.filter(projectBD__in=request.user.user_projBDs)
            else:
                raise InvestError(2009)
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
            elif request.user.has_perm('BD.user_manageProjectBD', bdinstance):
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

    @loginTokenIsAvailable(['BD.manageProjectBD'])
    def destroy(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                instance = self.get_object()
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
    username = RelationFilter(filterstr='username', lookup_method='icontains')
    usermobile = RelationFilter(filterstr='usermobile', lookup_method='contains')
    manager = RelationFilter(filterstr='manager',lookup_method='in')
    bd_status = RelationFilter(filterstr='bd_status', lookup_method='in')
    class Meta:
        model = OrgBD
        fields = ('username','usermobile','manager','bd_status')


class OrgBDView(viewsets.ModelViewSet):
    """
    list:获取机构BD
    create:增加机构BD
    retrieve:查看机构BD信息
    update:修改机构BD信息
    destroy:删除机构BD
    """
    filter_backends = (filters.DjangoFilterBackend,filters.SearchFilter)
    queryset = OrgBD.objects.filter(is_deleted=False)
    filter_class = OrgBDFilter
    search_fields = ('proj__projtitleC', 'username','manager__usernameC',)
    serializer_class = OrgBDSerializer

    def get_queryset(self):
        assert self.queryset is not None, (
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method."
            % self.__class__.__name__
        )
        queryset = self.queryset
        if isinstance(queryset, QuerySet):
            if self.request.user.is_authenticated:
                queryset = queryset.filter(datasource=self.request.user.datasource_id)
            else:
                queryset = queryset
        else:
            raise InvestError(code=8890)
        return queryset



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
            if request.user.has_perm('BD.manageOrgBD'):
                pass
            elif request.user.has_perm('BD.user_getOrgBD'):
                queryset = queryset.filter(Q(manager=request.user) | Q(proj__in=request.user.usertake_projs.all()) | Q(proj__in=request.user.usermake_projs.all()))
            else:
                raise InvestError(2009)
            countres = queryset.values_list('manager').annotate(Count('manager'))
            countlist = []
            for manager_count in countres:
                countlist.append({'manager':manager_count[0],'count':manager_count[1]})
            sortfield = request.GET.get('sort', 'createdtime')
            desc = request.GET.get('desc', 1)
            if desc in ('1', u'1', 1):
                sortfield = '-' + sortfield
            queryset = queryset.order_by('-isimportant', sortfield)
            try:
                count = queryset.count()
                queryset = Paginator(queryset, page_size)
                queryset = queryset.page(page_index)
            except EmptyPage:
                return JSONResponse(SuccessResponse({'count': 0, 'data': [], 'manager_count':countlist}))
            serializer = OrgBDSerializer(queryset, many=True)
            return JSONResponse(SuccessResponse({'count':count,'data':returnListChangeToLanguage(serializer.data,lang), 'manager_count':countlist}))
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
            if request.user.has_perm('BD.manageOrgBD'):
                pass
            else:
                proj = data.get('proj', None)
                if proj:
                    projinstance = project.objects.get(id=proj, is_deleted=False, datasource=request.user.datasource)
                    if request.user not in [projinstance.takeUser, projinstance.makeUser]:
                        raise InvestError(2009)
                else:
                    raise InvestError(2009)
            with transaction.atomic():
                orgBD = OrgBDCreateSerializer(data=data)
                if orgBD.is_valid():
                    neworgBD = orgBD.save()
                    if neworgBD.manager:
                        add_perm('BD.user_manageOrgBD', neworgBD.manager, neworgBD)
                else:
                    raise InvestError(5004,msg='机构BD创建失败——%s'%orgBD.error_messages)
                if comments:
                    data['orgBD'] = neworgBD.id
                    commentinstance = OrgBDCommentsCreateSerializer(data=data)
                    if commentinstance.is_valid():
                        commentinstance.save()
                sendmessage_orgBDMessage(neworgBD, receiver=neworgBD.manager,
                                    types=['app', 'webmsg', 'sms'], sender=request.user)
                return JSONResponse(SuccessResponse(returnDictChangeToLanguage(OrgBDSerializer(neworgBD).data,lang)))
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
            oldmanager = instance.manager
            data.pop('createuser', None)
            data.pop('datasource', None)
            if request.user.has_perm('BD.manageOrgBD'):
                pass
            elif request.user.has_perm('BD.user_manageOrgBD', instance):
                data = {'bd_status': data.get('bd_status', instance.bd_status_id)}
            else:
                raise InvestError(2009)
            with transaction.atomic():
                orgBD = OrgBDCreateSerializer(instance,data=data)
                if orgBD.is_valid():
                    neworgBD = orgBD.save()
                    oldmanager_id = data.get('manager', None)
                    if oldmanager_id and oldmanager_id != oldmanager.id:
                        add_perm('BD.user_manageOrgBD', neworgBD.manager, neworgBD)
                        rem_perm('BD.user_manageOrgBD', oldmanager, neworgBD)
                        sendmessage_orgBDMessage(neworgBD, receiver=neworgBD.manager,
                                                 types=['app', 'wenmsg', 'sms'], sender=request.user)
                else:
                    raise InvestError(5004, msg='机构BD修改失败——%s' % orgBD.error_messages)
                return JSONResponse(
                    SuccessResponse(returnDictChangeToLanguage(OrgBDSerializer(neworgBD).data, lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))


    @loginTokenIsAvailable(['BD.manageOrgBD',])
    def destroy(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                instance = self.get_object()
                instance.is_deleted = True
                instance.deleteduser = request.user
                instance.deletedtime = datetime.datetime.now()
                instance.save()
                instance.OrgBD_comments.filter(is_deleted=False).update(is_deleted=True, deleteduser=request.user,
                                                                        deletedtime=datetime.datetime.now())
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
                queryset = queryset.filter(datasource=self.request.user.datasource_id)
            else:
                queryset = queryset
        else:
            raise InvestError(code=8890)
        return queryset



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
            if request.user.has_perm('BD.manageOrgBD'):
                pass
            elif request.user.has_perm('BD.user_manageOrgBD'):
                queryset = queryset.filter(orgBD__in=request.user.user_orgBDs.all())
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
            bdinstance = ProjectBD.objects.get(id=int(data['orgBD']))
            if request.user.has_perm('BD.manageOrgBD'):
                pass
            elif request.user.has_perm('BD.user_manageOrgBD', bdinstance):
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
                else:
                    raise InvestError(5004, msg='创建机构BDcomments失败--%s' % commentinstance.error_messages)
                return JSONResponse(SuccessResponse(returnDictChangeToLanguage(OrgBDCommentsSerializer(newcommentinstance).data, lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))


    @loginTokenIsAvailable(['BD.manageOrgBD'])
    def destroy(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                instance = self.get_object()
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


class MeetingBDView(viewsets.ModelViewSet):
    """
    list:获取会议BD
    create:增加会议BD
    retrieve:查看会议BD信息
    update:修改会议BD信息
    destroy:删除会议BD
    """
    filter_backends = (filters.DjangoFilterBackend,filters.SearchFilter)
    queryset = MeetingBD.objects.filter(is_deleted=False)
    filter_fields = ('username','usermobile','manager')
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
                queryset = queryset.filter(datasource=self.request.user.datasource_id)
            else:
                queryset = queryset
        else:
            raise InvestError(code=8890)
        return queryset


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
            if request.user.has_perm('BD.manageMeetBD'):
                pass
            elif request.user.has_perm('BD.user_getMeetBD'):
                queryset = queryset.filter(Q(manager=request.user) | Q(proj__in=request.user.usertake_projs.all()) | Q(proj__in=request.user.usermake_projs.all()))
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


    @loginTokenIsAvailable(['BD.manageMeetBD',])
    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            lang = request.GET.get('lang')
            data['createuser'] = request.user.id
            data['datasource'] = request.user.datasource.id
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
                data = {'comments': data.get('comments', instance.comments),
                        'attachment': data.get('attachment', instance.attachment),
                        'attachmentbucket': data.get('attachmentbucket', instance.attachmentbucket),}
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


    @loginTokenIsAvailable(['BD.manageMeetBD',])
    def destroy(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                instance = self.get_object()
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
