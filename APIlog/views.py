import datetime
from django.shortcuts import render

# Create your views here.
from APIlog.models import loginlog, userviewprojlog, APILog


def logininlog(loginaccount,logintypeid,datasourceid,userid=None):
    if isinstance(logintypeid,str):
        logintypeid = int(logintypeid)
    loginlog(loginaccount=loginaccount,logintype=logintypeid,datasource=datasourceid,user=userid).save()

def viewprojlog(userid,projid,sourceid):
    userviewprojlog(user=userid,proj=projid,source=sourceid).save()

def apilog(request,modeltype,request_before,request_after,modelID=None,datasource=None):
    if request.META.has_key('HTTP_X_FORWARDED_FOR'):
        ip = request.META['HTTP_X_FORWARDED_FOR']
    else:
        ip = request.META['REMOTE_ADDR']
    url = request.get_full_path()
    method = request.method
    requestbody = request.body
    if request.user.is_anonymous:
        requestuser = None
        datasource = datasource
    else:
        requestuser = request.user.id
        datasource = request.user.datasource_id
    APILog(IPaddress=ip,URL=url,method=method,requestbody=requestbody,requestuser=requestuser,
           modeltype=modeltype,modelID=modelID,request_before=request_before,request_after=request_after,datasource=datasource).save()