#coding=utf-8
from django.core.paginator import Paginator, EmptyPage
from django.db import transaction
from rest_framework import filters
from rest_framework.viewsets import GenericViewSet
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import api_view

from proj.models import project, finance, favorite
from proj.serializer import ProjSerializer, FavoriteSerializer,FormatSerializer,FinanceSerializer
from usersys.models import MyUser
from utils.util import JSONResponse, catchexcption, read_from_cache, write_to_cache, successresponse, \
    loginTokenIsAvailable


class ProjectView(viewsets.ModelViewSet):
    filter_backends = (filters.SearchFilter, filters.DjangoFilterBackend,)
    queryset = project.objects.filter(is_deleted=False)
    filter_fields = ('titleC', 'titleE',)
    search_fields = ('titleC', 'titleE')
    serializer_class = ProjSerializer
    redis_key = 'project'
    Model = project

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
                raise ValueError('obj with this "%s" is not exist' % self.kwargs[lookup_url_kwarg])
            else:
                write_to_cache(self.redis_key + '_%s' % self.kwargs[lookup_url_kwarg], obj)
        return obj

    def list(self, request, *args, **kwargs):
        page_size = request.GET.get('page_size')
        page_index = request.GET.get('page_index')  # 从第一页开始
        if not page_size:
            page_size = 10
        if not page_index:
            page_index = 1
        queryset = self.filter_queryset(self.queryset)
        #加权限，筛选结果集
        try:
            queryset = Paginator(queryset, page_size)
        except EmptyPage:
            return JSONResponse({'success': True, 'result': None, 'count': 0})
        queryset = queryset.page(page_index)
        serializer = self.get_serializer(queryset, many=True)
        successresponse['result'] = serializer.data
        return JSONResponse(successresponse)

    @loginTokenIsAvailable(['上传项目权限'])
    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            projdata = data.get('proj')
            financesdata = data.get('finances')
            formatdata = data.get('format')
            proj = ProjSerializer(projdata)
            if proj.is_valid():
                proj.save()
            finances = FinanceSerializer(financesdata,many=True)
            if finances.is_valid():
                finances.save()
            format = FormatSerializer(formatdata)
            if format.is_valid():
                format.save()


            successresponse['result'] = UserSerializer(user).data
            return JSONResponse(successresponse)

        except Exception:
            catchexcption(request)
            return JSONResponse(failresponse)

