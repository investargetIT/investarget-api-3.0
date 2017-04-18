
from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer


class JSONResponse(HttpResponse):
    def __init__(self,data, **kwargs):
        content = JSONRenderer().render(data=data)
        kwargs['content_type'] = 'application/json; charset=utf-8'
        super(JSONResponse, self).__init__(content , **kwargs)

class InvestError(Exception):
    def __init__(self, code=None, msg=None):
        Exception.__init__(self)
        self.code = code
        self.msg = msg