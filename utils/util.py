#coding=utf-8
from rest_framework import status
from rest_framework.views import exception_handler
from django.core.cache import cache
from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer
import datetime
import traceback

from usersys.models import MyToken

REDIS_TIMEOUT = 1 * 24 * 60 * 60

weixinfilepath = '/Users/investarget/Desktop/django_server/third_header/weixin'
linkedinfilepath = '/Users/investarget/Desktop/django_server/third_header/Linkedin'
excptionlogpath = '/Users/investarget/Desktop/django_server/excption_log'




#读
def read_from_cache(key):
    value = cache.get(key)
    return value
#写
def write_to_cache(key ,value):
    cache.set(key, value, REDIS_TIMEOUT)


#删除
def cache_clearALL():
    cache.clear()
#删除
def cache_delete_key(key):
    cache.delete(key)



permissiondeniedresponse = {
                'success':False,
                'result': None,
                'error': '没有权限',
            }

successresponse = {
                'success':True,
                'result': None,
                'error': None,
}

failresponse = {
                'success':False,
                'result': None,
                'error': traceback.format_exc().split('\n')[-2],
}



def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    if response is not None:
        response.data['status_code'] = response.status_code

    return response

#记录request error
def catchexcption(request):
    now = datetime.datetime.now()
    filepath = excptionlogpath + '/' + now.strftime('%Y-%m-%d')
    f = open(filepath, 'a')
    f.writelines(now.strftime('%H:%M:%S')+'  user_agent:'+request.META['HTTP_USER_AGENT']+ '  请求发起用户id:'+str(request.user.id)+'  path: '+request.path+ '\n'+ traceback.format_exc()+'\n\n')
    f.close()

#记录error
def logexcption():
    now = datetime.datetime.now()
    filepath = excptionlogpath + '/' + now.strftime('%Y-%m-%d')
    f = open(filepath, 'a')
    f.writelines(now.strftime('%H:%M:%S')+'\n'+ traceback.format_exc()+'\n\n')
    f.close()


class JSONResponse(HttpResponse):
    def __init__(self,data, **kwargs):
        content = JSONRenderer().render(data=data)
        kwargs['content_type'] = 'application/json; charset=utf-8'
        super(JSONResponse, self).__init__(content , **kwargs)

def loginTokenIsAvailable(permissions=None):#判断model级别权限
    def token_available(func):
        def _token_available(self,request, *args, **kwargs):
            try:
                tokenkey = request.META.get('HTTP_TOKEN')
                if tokenkey:
                    token = MyToken.objects.get(key=tokenkey,isdeleted=False)
                else:
                    permissiondeniedresponse['error'] = '没有认证token'
                    return JSONResponse(permissiondeniedresponse)
            except Exception as exc:
                return JSONResponse(failresponse)
            else:
                if token.created.replace(tzinfo=None) < datetime.datetime.utcnow() - datetime.timedelta(hours=24 * 1):
                    permissiondeniedresponse['error'] = 'token过期'
                    return JSONResponse(permissiondeniedresponse)
                request.user = token.user
                user_has_permissions = []
                if permissions:
                    for permission in permissions:
                        if request.user.has_perm(permission):
                            user_has_permissions.append(permission)
                    if not user_has_permissions:
                        return JSONResponse({'result': None, 'success': False, 'error': '没有权限'})
                kwargs['permissions'] = user_has_permissions
                return func(self,request, *args, **kwargs)

        return _token_available
    return token_available

