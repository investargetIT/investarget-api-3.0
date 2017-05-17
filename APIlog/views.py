from django.shortcuts import render

# Create your views here.
from APIlog.models import loginlog, userviewprojlog


def logininlog(loginaccount,loginsource,userid=None):
    loginlog(loginaccount=loginaccount,loginsource=loginsource,user=userid).save()

def viewprojlog(userid,projid,sourceid):
    userviewprojlog(user=userid,proj=projid,source=sourceid).save()