from __future__ import unicode_literals

from django.db import models

# Create your models here.
from usersys.models import MyUser
from utils.customClass import MyForeignKey


class activity(models.Model):
    id = models.AutoField(primary_key=True)
    titleC = models.CharField(max_length=128,blank=True,null=True)
    titleE = models.TextField(blank=True,null=True)
    bucket = models.CharField(max_length=16)
    key = models.CharField(max_length=64)
    index = models.SmallIntegerField(blank=True,null=True)
    detailUrl = models.URLField()
    isActive = models.BooleanField(blank=True,default=True)
    isNews = models.BooleanField(blank=True,default=False)
    is_deleted = models.BooleanField(blank=True, default=False)
    deleteduser = MyForeignKey(MyUser,blank=True,null=True,related_name='userdelete_activities',on_delete=models.SET_NULL)
    deletedtime = models.DateTimeField(blank=True,null=True)
    createdtime = models.DateTimeField(auto_now_add=True, null=True)
    createuser = MyForeignKey(MyUser,blank=True,null=True,related_name='usercreate_activities',on_delete=models.SET_NULL)
    lastmodifytime = models.DateTimeField(auto_now=True)
    lastmodifyuser = MyForeignKey(MyUser, blank=True, null=True, related_name='usermodify_activities', on_delete=models.SET_NULL)
    class Meta:
        db_table = 'activity'
