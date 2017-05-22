import datetime
from django.shortcuts import render

# Create your views here.
from APIlog.models import loginlog, userviewprojlog, APILog


def logininlog(loginaccount,loginsource,userid=None):
    loginlog(loginaccount=loginaccount,loginsource=loginsource,user=userid).save()

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




    # IPaddress = models.CharField(max_length=32,blank=True,null=True)
    # URL = models.CharField(max_length=128,blank=True,null=True)
    # method = models.CharField(max_length=16,blank=True,null=True)
    # requestbody = models.TextField()
    # requestuser = models.IntegerField(blank=True,null=True)
    # modeltype = models.CharField(max_length=32,blank=True,null=True)
    # modelID = models.IntegerField(blank=True,null=True)
    # request_before = models.TextField(blank=True,null=True)
    # request_after = models.TextField(blank=True,null=True)
    # actiontime = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    # is_deleted = models.BooleanField(blank=True,default=False)