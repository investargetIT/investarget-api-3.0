#coding=utf-8

from django.core.cache import cache
import datetime
import traceback

from usersys.models import MyToken
from usersys.serializer import UserListSerializer
from utils.myClass import JSONResponse

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

#记录request error
def catchexcption(request):
    now = datetime.datetime.now()
    #filepath = excptionlogpath + '/' + now.strftime('%Y-%m-%d')
    #f = open(filepath, 'a')
    #f.writelines(now.strftime('%H:%M:%S')+'  user_agent:'+request.META['HTTP_USER_AGENT']+ '  请求发起用户id:'+str(request.user.id)+'  path: '+request.path+ '\n'+ traceback.format_exc()+'\n\n')
    #f.close()

#记录error
def logexcption():
    now = datetime.datetime.now()
    filepath = excptionlogpath + '/' + now.strftime('%Y-%m-%d')
    f = open(filepath, 'a')
    f.writelines(now.strftime('%H:%M:%S')+'\n'+ traceback.format_exc()+'\n\n')
    f.close()


def loginTokenIsAvailable(permissions=None):#判断model级别权限
    def token_available(func):
        def _token_available(self,request, *args, **kwargs):
            try:
                tokenkey = request.META.get('HTTP_TOKEN')
                if tokenkey:
                    token = MyToken.objects.get(key=tokenkey,is_deleted=False)
                else:
                    return JSONResponse({'result': None, 'success': False, 'errorcode':3000,'errormsg':None})
            except Exception as exc:
                return JSONResponse({'success':False,'result': None,'errorcode': 3000,'errormsg':repr(exc)})
            else:
                if token.created < datetime.datetime.now() - datetime.timedelta(hours=24 * 1):
                    return JSONResponse({'result': None, 'success': False, 'errorcode':3000,'errormsg':None})
                request.user = token.user
                user_has_permissions = []
                if permissions:
                    for permission in permissions:
                        if request.user.has_perm(permission):
                            user_has_permissions.append(permission)
                    if not user_has_permissions:
                        return JSONResponse({'result': None, 'success': False, 'errorcode':2009,'errormsg':None})
                kwargs['permissions'] = user_has_permissions
                return func(self,request, *args, **kwargs)

        return _token_available
    return token_available

def maketoken(user,clienttype):
    try:
        tokens = MyToken.objects.filter(user=user, clienttype_id=clienttype, is_deleted=False)
    except MyToken.DoesNotExist:
        pass
    else:
        for token in tokens:
            token.is_deleted = True
            token.save(update_fields=['is_deleted'])
    token = MyToken.objects.create(user=user, clienttype_id=clienttype)
    serializer = UserListSerializer(user)
    response = serializer.data
    return {'token':token.key,
        "user_info": response,
    }
