from __future__ import unicode_literals

from django.db import models

# Create your models here.

# request.get_full_path

# class APILog(models.Model):
#     IPaddress = models.CharField(max_length=32,blank=True,null=True)
#     URL = models.URLField(blank=True,null=True)
#     method = models.CharField()
#     # requestbody =
#     # afterwards =
#     actiontime = models.DateTimeField(auto_now_add=True,null=True,blank=True)
#     is_deleted = models.BooleanField(blank=True,default=False)
#     class Meta:
#         db_table = 'API_LOG'



class loginlog(models.Model):
    user = models.PositiveIntegerField(blank=True,null=True)
    loginaccount = models.CharField(max_length=40,blank=True,null=True)
    logintime = models.DateTimeField(auto_now_add=True,blank=True,null=True)
    loginsource = models.PositiveSmallIntegerField(blank=True,null=True)
    is_deleted = models.BooleanField(blank=True,default=False)
    class Meta:
        db_table = 'LOG_login'

class userviewprojlog(models.Model):
    user = models.PositiveIntegerField(blank=True,null=True)
    proj = models.PositiveIntegerField(blank=True,null=True)
    viewtime = models.DateTimeField(auto_now_add=True,blank=True,null=True)
    source = models.PositiveSmallIntegerField(blank=True,null=True)
    is_deleted = models.BooleanField(blank=True,default=False)
    class Meta:
        db_table = 'LOG_userviewproject'