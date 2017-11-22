#coding=utf8
import traceback

from django.core.paginator import Paginator, EmptyPage
from django.db import transaction
from django.db.models import QuerySet
from django_filters import FilterSet

# Create your views here.
from rest_framework import filters, viewsets
from BD.models import ProjectBD, ProjectBDComments, OrgBDComments, OrgBD
from BD.serializers import ProjectBDSerializer, ProjectBDCreateSerializer, ProjectBDCommentsCreateSerializer, \
    ProjectBDCommentsSerializer, OrgBDCommentsSerializer, OrgBDCommentsCreateSerializer, OrgBDCreateSerializer, \
    OrgBDSerializer
from utils.customClass import RelationFilter, InvestError, JSONResponse
from utils.util import loginTokenIsAvailable, SuccessResponse, InvestErrorResponse, ExceptionResponse, \
    returnListChangeToLanguage, catchexcption, returnDictChangeToLanguage


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


    #获取收藏列表，GET参数'user'，'trader'，'favoritetype'
    @loginTokenIsAvailable(['BD.getProjectBD','BD.manageProjectBD'])
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
            try:
                count = queryset.count()
                queryset = Paginator(queryset, page_size)
                queryset = queryset.page(page_index)
            except EmptyPage:
                return JSONResponse(SuccessResponse({'count': 0, 'data': []}))
            serializer = ProjectBDSerializer(queryset, many=True)
            return JSONResponse(SuccessResponse({'count':count,'data':returnListChangeToLanguage(serializer.data,lang)}))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    # 批量增加，接受modeldata，proj=projs=projidlist
    @loginTokenIsAvailable(['BD.manageProjectBD',])
    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            lang = request.GET.get('lang')
            comments = data.get('comments',None)
            data['createuser'] = request.user.id
            data['datasource'] = request.user.datasource.id
            with transaction.atomic():
                projectBD = ProjectBDCreateSerializer(data=data)
                if projectBD.is_valid():
                    newprojectBD = projectBD.save()
                else:
                    raise InvestError(4009,msg='项目BD创建失败——%s'%projectBD.error_messages)
                if comments:
                    data['projectBD'] = newprojectBD.id
                    commentinstance = ProjectBDCommentsCreateSerializer(data=data)
                    if commentinstance.is_valid():
                        commentinstance.save()
                return JSONResponse(SuccessResponse(returnListChangeToLanguage(ProjectBDSerializer(newprojectBD).data,lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable(['BD.getProjectBD','BD.manageProjectBD'])
    def retrieve(self, request, *args, **kwargs):
        try:
            lang = request.GET.get('lang')
            instance = self.get_object()
            serializer = self.serializer_class(instance)
            return JSONResponse(SuccessResponse(returnDictChangeToLanguage(serializer.data, lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable(['BD.manageProjectBD',])
    def update(self, request, *args, **kwargs):
        try:
            data = request.data
            lang = request.GET.get('lang')
            instance = self.get_object()
            data['createuser'] = request.user.id
            data['datasource'] = request.user.datasource.id
            with transaction.atomic():
                projectBD = ProjectBDCreateSerializer(instance,data=data)
                if projectBD.is_valid():
                    newprojectBD = projectBD.save()
                else:
                    raise InvestError(4009, msg='项目BD修改失败——%s' % projectBD.error_messages)
                return JSONResponse(
                    SuccessResponse(returnListChangeToLanguage(ProjectBDSerializer(newprojectBD).data, lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    #批量删除（参数传收藏model的idlist）
    @loginTokenIsAvailable(['BD.manageProjectBD',])
    def destroy(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                instance = self.get_object()
                # instance.is_deleted = True
                # instance.deleteduser = request.user
                # instance.deletedtime = datetime.datetime.now()
                # instance.save()
                instance.delete()
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

    @loginTokenIsAvailable(['BD.getProjectBD','BD.manageProjectBD'])
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

    @loginTokenIsAvailable(['BD.manageProjectBD'])
    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            lang = request.GET.get('lang')
            data['createuser'] = request.user.id
            data['datasource'] = request.user.datasource.id
            with transaction.atomic():
                commentinstance = ProjectBDCommentsCreateSerializer(data=data)
                if commentinstance.is_valid():
                    newcommentinstance = commentinstance.save()
                else:
                    raise InvestError(4009, msg='创建项目BDcomments失败--%s' % commentinstance.error_messages)
                return JSONResponse(SuccessResponse(returnListChangeToLanguage(ProjectBDCommentsSerializer(newcommentinstance).data, lang)))
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
                # instance.is_deleted = True
                # instance.deleteduser = request.user
                # instance.deletedtime = datetime.datetime.now()
                # instance.save()
                instance.delete()
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
    search_fields = ('usermobile', 'username')
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


    #获取收藏列表，GET参数'user'，'trader'，'favoritetype'
    @loginTokenIsAvailable(['BD.getOrgBD','BD.manageOrgBD'])
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
            try:
                count = queryset.count()
                queryset = Paginator(queryset, page_size)
                queryset = queryset.page(page_index)
            except EmptyPage:
                return JSONResponse(SuccessResponse({'count': 0, 'data': []}))
            serializer = OrgBDSerializer(queryset, many=True)
            return JSONResponse(SuccessResponse({'count':count,'data':returnListChangeToLanguage(serializer.data,lang)}))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    # 批量增加，接受modeldata，proj=projs=projidlist
    @loginTokenIsAvailable(['BD.manageOrgBD',])
    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            lang = request.GET.get('lang')
            comments = data.get('comments',None)
            data['createuser'] = request.user.id
            data['datasource'] = request.user.datasource.id
            with transaction.atomic():
                orgBD = OrgBDCreateSerializer(data=data)
                if orgBD.is_valid():
                    neworgBD = orgBD.save()
                else:
                    raise InvestError(5004,msg='机构BD创建失败——%s'%orgBD.error_messages)
                if comments:
                    data['orgBD'] = neworgBD.id
                    commentinstance = OrgBDCommentsCreateSerializer(data=data)
                    if commentinstance.is_valid():
                        commentinstance.save()
                return JSONResponse(SuccessResponse(returnListChangeToLanguage(OrgBDSerializer(neworgBD).data,lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable(['BD.getOrgBD','BD.manageOrgBD'])
    def retrieve(self, request, *args, **kwargs):
        try:
            lang = request.GET.get('lang')
            instance = self.get_object()
            serializer = self.serializer_class(instance)
            return JSONResponse(SuccessResponse(returnDictChangeToLanguage(serializer.data, lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable(['BD.manageOrgBD',])
    def update(self, request, *args, **kwargs):
        try:
            data = request.data
            lang = request.GET.get('lang')
            instance = self.get_object()
            data['createuser'] = request.user.id
            data['datasource'] = request.user.datasource.id
            with transaction.atomic():
                orgBD = OrgBDCreateSerializer(instance,data=data)
                if orgBD.is_valid():
                    neworgBD = orgBD.save()
                else:
                    raise InvestError(5004, msg='机构BD修改失败——%s' % orgBD.error_messages)
                return JSONResponse(
                    SuccessResponse(returnListChangeToLanguage(OrgBDSerializer(neworgBD).data, lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    #批量删除（参数传收藏model的idlist）
    @loginTokenIsAvailable(['BD.manageOrgBD',])
    def destroy(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                instance = self.get_object()
                # instance.is_deleted = True
                # instance.deleteduser = request.user
                # instance.deletedtime = datetime.datetime.now()
                # instance.save()
                instance.delete()
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


    # 获取收藏列表，GET参数'user'，'trader'，'favoritetype'
    @loginTokenIsAvailable(['BD.getOrgBD','BD.manageOrgBD'])
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

    # 批量增加，接受modeldata，proj=projs=projidlist
    @loginTokenIsAvailable(['BD.manageOrgBD'])
    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            lang = request.GET.get('lang')
            data['createuser'] = request.user.id
            data['datasource'] = request.user.datasource.id
            with transaction.atomic():
                commentinstance = OrgBDCommentsCreateSerializer(data=data)
                if commentinstance.is_valid():
                    newcommentinstance = commentinstance.save()
                else:
                    raise InvestError(5004, msg='创建机构BDcomments失败--%s' % commentinstance.error_messages)
                return JSONResponse(SuccessResponse(returnListChangeToLanguage(OrgBDCommentsSerializer(newcommentinstance).data, lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    # 批量删除（参数传收藏model的idlist）
    @loginTokenIsAvailable(['BD.manageOrgBD'])
    def destroy(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                instance = self.get_object()
                # instance.is_deleted = True
                # instance.deleteduser = request.user
                # instance.deletedtime = datetime.datetime.now()
                # instance.save()
                instance.delete()
            return JSONResponse(SuccessResponse({'isDeleted': True, }))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))