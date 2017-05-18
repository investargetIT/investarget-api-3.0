#coding=utf-8

from django.core.cache import cache
import datetime
import traceback

from usersys.models import MyToken
from usersys.serializer import UserListSerializer
from utils.customClass import JSONResponse, InvestError

REDIS_TIMEOUT = 1 * 24 * 60 * 60
weixinfilepath = '/Users/investarget/Desktop/django_server/third_header/weixin'
linkedinfilepath = '/Users/investarget/Desktop/django_server/third_header/Linkedin'
excptionlogpath = '/Users/investarget/Desktop/django_server/excption_log'

def SuccessResponse(data,msg=None):
    response = {'code':1000,'errormsg':msg,'result':data}
    return response
def InvestErrorResponse(err):
    response = {'code': err.code, 'errormsg': err.msg, 'result': None}
    return response
def ExceptionResponse(msg):
    response = {'code':9999, 'errormsg': msg, 'result': None}
    return response

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
    if request.META.has_key('HTTP_X_FORWARDED_FOR'):
        ip = request.META['HTTP_X_FORWARDED_FOR']
    else:
        ip = request.META['REMOTE_ADDR']
    filepath = excptionlogpath + '/' + now.strftime('%Y-%m-%d')
    f = open(filepath, 'a')
    f.writelines(now.strftime('%H:%M:%S') + '请求用户ip:%s'%ip +'  user_agent:'+request.META['HTTP_USER_AGENT']+ '  请求发起用户id:'+str(request.user.id)+'  path: '+request.path+ '\n'+ traceback.format_exc()+'\n\n')
    f.close()

#记录error
def logexcption():
    now = datetime.datetime.now()
    filepath = excptionlogpath + '/' + now.strftime('%Y-%m-%d')
    f = open(filepath, 'a')
    f.writelines(now.strftime('%H:%M:%S')+'\n'+ traceback.format_exc()+'\n\n')
    f.close()

def checkIPAddress(ip):
    key = 'ip_%s'%str(ip)
    times = cache.get(key)
    if times:
        times = times + 1
    else:
        times = 1
    cache.set(key, times, 60 * 60 * 1)
    return times

def loginTokenIsAvailable(permissions=None):#判断class级别权限
    def token_available(func):
        def _token_available(self,request, *args, **kwargs):
            try:
                tokenkey = request.META.get('HTTP_TOKEN')
                if tokenkey:
                    try:
                        token = MyToken.objects.get(key=tokenkey,is_deleted=False)
                    except MyToken.DoesNotExist:
                        return JSONResponse(InvestErrorResponse(InvestError(3000,msg='token不存在')))
                else:
                    return JSONResponse(InvestErrorResponse(InvestError(3000,msg='server error')))
            except Exception as exc:
                return JSONResponse(InvestErrorResponse(InvestError(code=3000,msg=repr(exc))))
            else:
                if token.created < datetime.datetime.now() - datetime.timedelta(hours=24 * 1):
                    return JSONResponse(InvestErrorResponse(InvestError(3000,msg='token过期')))
                request.user = token.user
                if token.user.is_deleted:
                    return JSONResponse(InvestErrorResponse(InvestError(3000,msg='用户不存在')))
                user_has_permissions = []
                if permissions:
                    for permission in permissions:
                        if request.user.has_perm(permission):
                            user_has_permissions.append(permission)
                    if not user_has_permissions:
                        return JSONResponse(InvestErrorResponse(InvestError(2009)))
                kwargs['permissions'] = user_has_permissions
                return func(self,request, *args, **kwargs)

        return _token_available
    return token_available

def checkrequesttoken(request):#判断token是否有效
    try:
        tokenkey = request.META.get('HTTP_TOKEN')
        if tokenkey:
            try:
                token = MyToken.objects.get(key=tokenkey, is_deleted=False)
            except MyToken.DoesNotExist:
                raise InvestError(3000, msg='token不存在')
        else:
            raise InvestError(3000, msg='NO TOKEN')
    except InvestError as err:
        raise err
    except Exception as exc:
        raise InvestError(code=3000, msg=repr(exc))
    else:
        if token.created < datetime.datetime.now() - datetime.timedelta(hours=24 * 1):
            raise InvestError(3000, msg='token过期')
        request.user = token.user
        if token.user.is_deleted:
            raise InvestError(3000, msg='用户不存在')




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

def returnDictChangeToLanguage(dictdata,lang=None):
    newdict = {}
    if lang == 'en':
        for key,value in dictdata.items():
            if key[-1] == 'E' and dictdata.has_key(key[0:-1]+'C'):
                newdict[key[0:-1]] = value
            elif key[-1] == 'C' and dictdata.has_key(key[0:-1]+'E'):
                pass
            else:
                if isinstance(value,dict):
                    newdict[key] = returnDictChangeToLanguage(value,lang=lang)
                elif isinstance(value,list):
                    newlist = []
                    for minvalues in value:
                        if isinstance(minvalues, dict):
                            newlist.append(returnDictChangeToLanguage(minvalues,lang=lang))
                        else:
                            newlist.append(minvalues)
                    newdict[key] = newlist
                else:
                    newdict[key] = value
    else:
        for key,value in dictdata.items():
            if key[-1] == 'E' and dictdata.has_key(key[0:-1]+'C'):
                pass
            elif key[-1] == 'C' and dictdata.has_key(key[0:-1]+'E'):
                newdict[key[0:-1]] = value
            else:
                if isinstance(value,dict):
                    newdict[key] = returnDictChangeToLanguage(value, lang=lang)
                elif isinstance(value,list):
                    newlist = []
                    for minvalues in value:
                        if isinstance(minvalues, dict):
                            newlist.append(returnDictChangeToLanguage(minvalues, lang=lang))
                        else:
                            newlist.append(minvalues)
                    newdict[key] = newlist
                else:
                    newdict[key] = value

    return newdict

#list内嵌dict
def returnListChangeToLanguage(listdata,lang=None):
    newlist = []
    for listone in listdata:
        if isinstance(listone,dict):
            newlist.append(returnDictChangeToLanguage(listone,lang=lang))
        else:
            newlist.append(listone)
    return newlist
