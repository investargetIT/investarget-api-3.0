
from django.http import HttpResponse
from rest_framework import filters
from rest_framework.permissions import BasePermission
from rest_framework.renderers import JSONRenderer


from utils.responsecode import responsecode


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
