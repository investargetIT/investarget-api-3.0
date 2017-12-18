#coding=utf-8

from django.core.cache import cache
import datetime
import traceback

from django.core.exceptions import FieldError
from guardian.shortcuts import assign_perm, remove_perm

from invest.settings import APILOG_PATH
from usersys.models import MyToken
from utils.customClass import JSONResponse, InvestError

REDIS_TIMEOUT = 1 * 24 * 60 * 60

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
def write_to_cache(key ,value, time_out=REDIS_TIMEOUT):
    cache.set(key, value, time_out)

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
    filepath = APILOG_PATH['excptionlogpath'] + '/' + now.strftime('%Y-%m-%d')
    f = open(filepath, 'a')
    f.writelines(now.strftime('%H:%M:%S') + '请求用户ip:%s'%ip +'  user_agent:'+request.META['HTTP_USER_AGENT']+ '  请求发起用户id:'+str(request.user.id)+'  path: '+request.path + 'method:' + request.method +'\n'+ traceback.format_exc()+'\n\n')
    f.close()

#记录error
def logexcption(msg=None):
    now = datetime.datetime.now()
    filepath = APILOG_PATH['excptionlogpath'] + '/' + now.strftime('%Y-%m-%d')
    f = open(filepath, 'a')
    f.writelines(now.strftime('%H:%M:%S')+'\n'+ traceback.format_exc()+ msg if msg else ' ' +'\n\n')
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
#检查view内 request的token
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
                    return JSONResponse(InvestErrorResponse(InvestError(3000,msg='token缺失')))
            except Exception as exc:
                return JSONResponse(InvestErrorResponse(InvestError(code=3000,msg=repr(exc))))
            else:
                if token.timeout():
                    return JSONResponse(InvestErrorResponse(InvestError(3000,msg='token过期')))
                if token.user.is_deleted:
                    return JSONResponse(InvestErrorResponse(InvestError(3000,msg='用户不存在')))
                request.user = token.user
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

#检查def request的token
def checkRequestToken():
    def token_available(func):
        def _token_available(request, *args, **kwargs):
            try:
                tokenkey = request.META.get('HTTP_TOKEN')
                if tokenkey:
                    try:
                        token = MyToken.objects.get(key=tokenkey,is_deleted=False)
                    except MyToken.DoesNotExist:
                        return JSONResponse(InvestErrorResponse(InvestError(3000,msg='token不存在')))
                    else:
                        if token.timeout():
                            return JSONResponse(InvestErrorResponse(InvestError(3000, msg='token过期')))
                        if token.user.is_deleted:
                            return JSONResponse(InvestErrorResponse(InvestError(3000, msg='用户不存在')))
                        request.user = token.user
                        return func(request, *args, **kwargs)
                else:
                    return JSONResponse(InvestErrorResponse(InvestError(3000,msg='token缺失')))
            except Exception as exc:
                return JSONResponse(InvestErrorResponse(InvestError(code=3000,msg=repr(exc))))
        return _token_available
    return token_available


def checkrequesttoken(token):#验证token有效
    if token:
        try:
            token = MyToken.objects.get(key=token, is_deleted=False)
        except MyToken.DoesNotExist:
            raise InvestError(3000, msg='token不存在')
        else:
            if token.timeout():
                raise InvestError(3000, msg='token过期')
            if token.user.is_deleted:
                raise InvestError(3000, msg='用户不存在')
            return token.user
    else:
        raise InvestError(3000, msg='NO TOKEN')


def setrequestuser(request):#根据token设置request.user
    tokenkey = request.META.get('HTTP_TOKEN', None)
    if tokenkey:
        try:
            token = MyToken.objects.get(key=tokenkey, is_deleted=False)
            if not token.timeout():
                request.user = token.user
        except MyToken.DoesNotExist:
            pass
        except Exception as err:
            raise InvestError(3000,msg=repr(err))
    else:
        pass

def add_perm(perm,user_or_group,obj=None):
    if user_or_group:
        assign_perm(perm,user_or_group,obj)
def rem_perm(perm,user_or_group,obj=None):
    if user_or_group:
        remove_perm(perm,user_or_group,obj)


def setUserObjectPermission(user,obj,permissions,touser=None):
    if touser is None:
        for permission in permissions:
            add_perm(permission, user, obj)
    else:
        for permission in permissions:
            rem_perm(permission, user, obj)
            add_perm(permission, touser, obj)


def returnDictChangeToLanguage(dictdata,lang=None):
    newdict = {'timezone':'+08:00'}
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
    elif lang == 'cn':
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
    else:
        newdict = dictdata
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


def requestDictChangeToLanguage(model,dictdata,lang=None):
    modelfields = model._meta.fields
    if not isinstance(modelfields,list):
        return  dictdata
    newdict = {}
    if lang == 'en':
        for key, value in dictdata.items():
            if (key + 'E') in modelfields and (key + 'C') in modelfields:
                newdict[key[0:-1] + 'E'] = value
            else:
                newdict[key] = value
    else:
        for key, value in dictdata.items():
            if dictdata.has_key(key + 'E') and dictdata.has_key(key + 'C'):
                newdict[key[0:-1] + 'E'] = value
            else:
                newdict[key] = value
    return newdict


def mySortQuery(queryset,sortfield,desc):
    '''

    :param queryset: 排序集合，queryset类型
    :param sortfield: 排序字段，str类型
    :param desc: 正反序
    :return: queryset类型
    '''
    try:
        if desc in ('1', u'1', 1):
            sortfield = '-' + sortfield
        queryset = queryset.order_by(sortfield)
        return queryset
    except FieldError:
        raise InvestError(8891,msg='无效字段')