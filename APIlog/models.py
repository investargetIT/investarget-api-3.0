from __future__ import unicode_literals

import datetime
from django.db import models

# Create your models here.



class APILog(models.Model):
    IPaddress = models.CharField(max_length=32,blank=True,null=True)
    URL = models.CharField(max_length=128,blank=True,null=True)
    method = models.CharField(max_length=16,blank=True,null=True)
    requestbody = models.TextField()
    requestuser_id = models.IntegerField(blank=True,null=True)
    requestuser_name = models.CharField(max_length=64,blank=True, null=True)
    modeltype = models.CharField(max_length=32,blank=True,null=True)
    model_id = models.IntegerField(blank=True,null=True)
    model_name = models.TextField(blank=True,null=True)
    request_before = models.TextField(blank=True,null=True)
    request_after = models.TextField(blank=True,null=True)
    actiontime = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    is_deleted = models.BooleanField(blank=True,default=False)
    datasource = models.PositiveSmallIntegerField(blank=True,default=1)
    class Meta:
        db_table = 'API_LOG'
    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.actiontime:
            self.actiontime = datetime.datetime.now()
        super(APILog,self).save(force_insert,force_update,using,update_fields)



class loginlog(models.Model):
    user = models.IntegerField(blank=True,null=True)
    ipaddress = models.CharField(max_length=20,blank=True,null=True)
    loginaccount = models.CharField(max_length=40,blank=True,null=True)
    logintime = models.DateTimeField(auto_now_add=True,blank=True,null=True)
    logintype = models.PositiveSmallIntegerField(blank=True,null=True)
    is_deleted = models.BooleanField(blank=True,default=False)
    datasource = models.PositiveSmallIntegerField(blank=True, default=1)
    class Meta:
        db_table = 'LOG_login'

class userviewprojlog(models.Model):
    user = models.IntegerField(blank=True,null=True)
    proj = models.IntegerField(blank=True,null=True)
    viewtime = models.DateTimeField(auto_now_add=True,blank=True,null=True)
    source = models.PositiveSmallIntegerField(blank=True,null=True)
    is_deleted = models.BooleanField(blank=True,default=False)
    datasource = models.PositiveSmallIntegerField(blank=True, default=1)
    class Meta:
        db_table = 'LOG_userviewproject'