
from django.http import HttpResponse
from rest_framework import filters
from rest_framework.renderers import JSONRenderer

from utils.responsecode import responsecode


class JSONResponse(HttpResponse):
    def __init__(self,data, **kwargs):
        content = JSONRenderer().render(data=data)
        kwargs['content_type'] = 'application/json; charset=utf-8'
        super(JSONResponse, self).__init__(content , **kwargs)

class InvestError(Exception):
    def __init__(self, code, msg=None):
        Exception.__init__(self)
        self.code = code
        if not msg:
           self.msg = responsecode[self.code]
        else:
           self.msg = msg


# class DataSourceFilter(filters.BaseFilterBackend):
#     def filter_queryset(self, request, queryset, view):
#         if hasattr(request.user,'datasource') and request.user.datasource:
#             queryset = queryset.all().filter(datasource=request.user.datasource)
#         return queryset