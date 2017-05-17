from utils.myClass import JSONResponse, InvestError
from utils.util import InvestErrorResponse

try:
    from django.utils.deprecation import MiddlewareMixin  # Django 1.10.x
except ImportError:
    MiddlewareMixin = object  # Django 1.4.x - Django 1.9.x

blackIPlist = []
class IpMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # clienttype = request.META.get('HTTP_CLIENTTYPE')
        # if clienttype and isinstance(clienttype,(str,int)) and clienttype in [1,2,3,4,'1','2','3','4']:
        #     pass
        # else:
        #     return JSONResponse(InvestErrorResponse(InvestError(code=3007)))
        if request.META.has_key('HTTP_X_FORWARDED_FOR'):
            ip = request.META['HTTP_X_FORWARDED_FOR']
        else:
            ip = request.META['REMOTE_ADDR']
        if ip:
            if ip in blackIPlist:
                return JSONResponse(InvestErrorResponse(InvestError(code=3005)))
            else:
                return None
        else:
            return JSONResponse(InvestErrorResponse(InvestError(code=3006)))
