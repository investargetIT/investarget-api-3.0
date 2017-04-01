from __future__ import unicode_literals

from django.db import models

# Create your models here.
from proj.models import project
from usersys.models import MyUser
from sourcetype.models import TransactionStatus

class timeline(models.Model):
    id = models.AutoField(primary_key=True)
    proj = models.ForeignKey(project,blank=True,null=True,related_name='proj_timelines')
    investor = models.ForeignKey(MyUser,blank=True,null=True,related_name='investor_timelines')
    supporter = models.ForeignKey(MyUser,blank=True,null=True,related_name='supporter_timelines')
    trader = models.ForeignKey(MyUser,blank=True,null=True,related_name='trader_timelines')
    isClose = models.BooleanField(blank=True,default=False)
    closeDate = models.DateTimeField(blank=True,null=True,)
    contractedServiceTime = models.DateTimeField(blank=True,null=True)
    turnoverTime = models.DateTimeField(blank=True,null=True)
    is_deleted = models.BooleanField(blank=True, default=False)
    deleteduser = models.ForeignKey(MyUser, blank=True, null=True, related_name='userdelete_timelines',on_delete=models.SET_NULL)
    deletedtime = models.DateTimeField(blank=True, null=True)
    createdtime = models.DateTimeField(auto_now_add=True)
    createuser = models.ForeignKey(MyUser, blank=True, null=True, related_name='usercreate_timelines',on_delete=models.SET_NULL)
    lastmodifytime = models.DateTimeField(auto_now=True)
    lastmodifyuser = models.ForeignKey(MyUser, blank=True, null=True, related_name='usermodify_timelines',on_delete=models.SET_NULL)
    class Meta:
        db_table = 'timeline'

class timelineTransationStatu(models.Model):
    id = models.AutoField(primary_key=True)
    timeline = models.ForeignKey(timeline,blank=True,null=True,related_name='timeline_transationStatus')
    transationStatus = models.ForeignKey(TransactionStatus,)
    isActive = models.BooleanField(blank=True,default=False)
    alertCycle = models.SmallIntegerField(blank=True,null=True)
    inDate = models.DateTimeField(blank=True,null=True)
    is_deleted = models.BooleanField(blank=True, default=False)
    deleteduser = models.ForeignKey(MyUser, blank=True, null=True, related_name='userdelete_timelinestatus',on_delete=models.SET_NULL)
    deletedtime = models.DateTimeField(blank=True, null=True)
    createdtime = models.DateTimeField(auto_now_add=True)
    createuser = models.ForeignKey(MyUser, blank=True, null=True, related_name='usercreate_timelinestatus',on_delete=models.SET_NULL)
    lastmodifytime = models.DateTimeField(auto_now=True)
    lastmodifyuser = models.ForeignKey(MyUser, blank=True, null=True, related_name='usermodify_timelinestatus',on_delete=models.SET_NULL)

    class Meta:
        db_table = 'timelineTransationStatus'

class timelineremark(models.Model):
    id = models.AutoField(primary_key=True)
    timeline = models.ForeignKey(timeline,related_name='timeline_remarks',blank=True,null=True)
    remark = models.TextField(blank=True,null=True)
    is_deleted = models.BooleanField(blank=True, default=False)
    deleteduser = models.ForeignKey(MyUser, blank=True, null=True, related_name='userdelete_timelineremarks',on_delete=models.SET_NULL)
    deletedtime = models.DateTimeField(blank=True, null=True)
    createdtime = models.DateTimeField(auto_now_add=True)
    createuser = models.ForeignKey(MyUser, blank=True, null=True, related_name='usercreate_timelineremarks',on_delete=models.SET_NULL)
    lastmodifytime = models.DateTimeField(auto_now=True)
    lastmodifyuser = models.ForeignKey(MyUser, blank=True, null=True, related_name='usermodify_timelineremarks', on_delete=models.SET_NULL)
    class Meta:
        db_table = 'timelineremarks'