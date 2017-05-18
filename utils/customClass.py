
from django.http import HttpResponse
from rest_framework import filters
from rest_framework.permissions import BasePermission
from rest_framework.renderers import JSONRenderer


from utils.responsecode import responsecode
from django_filters import Filter

class JSONResponse(HttpResponse):
    def __init__(self,data, **kwargs):
        content = JSONRenderer().render(data=data)
        kwargs['content_type'] = 'application/json; charset=utf-8'
        super(JSONResponse, self).__init__(content , **kwargs)

class InvestError(Exception):
    def __init__(self, code,msg=None):
        self.code = code
        if msg:
            self.msg = msg
        else:
            self.msg = responsecode[str(code)]

class IsSuperUser(BasePermission):
    """
    Allows access only to admin users.
    """
    def has_permission(self, request, view):
        return (
            request.method in ('GET', 'HEAD', 'OPTIONS') or
            request.user and
            request.user.is_superuser
        )
class RelationFilter(Filter):
    def __init__(self, filterstr,lookup_method, **kwargs):
        self.filterstr = filterstr
        self.lookup_method = lookup_method
        super(RelationFilter,self).__init__(**kwargs)
    def filter(self, qs, value):
        if value in ([], (), {}, '', None):
            return qs
        if self.lookup_method == 'in':
            value = value.split(',')
        return qs.filter(**{'%s__%s' % (self.filterstr,self.lookup_method): value}).distinct()