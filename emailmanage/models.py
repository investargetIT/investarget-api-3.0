#coding=utf-8
from __future__ import unicode_literals

from django.db import models

# Create your models here.



class emailgroupsendlist(models.Model):
    proj = models.IntegerField(blank=True,null=True,help_text='项目')
    projtitle = models.TextField(blank=True,null=True)
    user = models.IntegerField(blank=True,null=True,help_text='用户')
    username = models.CharField(max_length=64,blank=True,null=True)
    userEmail = models.CharField(max_length=64,blank=True,null=True)
    isRead = models.BooleanField(blank=True,default=False,help_text='用户是否已读')
    readtime = models.DateTimeField(blank=True,null=True)
    isSend = models.BooleanField(blank=True,default=False,help_text='是否发送邮件成功')
    sendtime = models.DateTimeField(auto_created=True,blank=True,null=True)
    errmsg = models.TextField(blank=True,null=True,help_text='发送失败原因')
    is_deleted = models.BooleanField(blank=True,default=False)
    datasource = models.IntegerField(blank=True,null=True)
