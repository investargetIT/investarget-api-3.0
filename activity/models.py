from __future__ import unicode_literals

import datetime
from django.db import models

# Create your models here.
from usersys.models import MyUser
from utils.customClass import MyForeignKey, MyModel


class activity(MyModel):
    id = models.AutoField(primary_key=True)
    titleC = models.CharField(max_length=128,blank=True,null=True)
    titleE = models.TextField(blank=True,null=True)
    bucket = models.CharField(max_length=16,blank=True,null=True)
    key = models.CharField(max_length=64,blank=True,null=True)
    index = models.SmallIntegerField(blank=True,null=True)
    detailUrl = models.URLField(blank=True,null=True)
    isActive = models.BooleanField(blank=True,default=True)
    isNews = models.BooleanField(blank=True,default=False)
    deleteduser = MyForeignKey(MyUser,blank=True,null=True,related_name='userdelete_activities')
    createuser = MyForeignKey(MyUser,blank=True,null=True,related_name='usercreate_activities')
    lastmodifyuser = MyForeignKey(MyUser, blank=True, null=True, related_name='usermodify_activities')
    class Meta:
        db_table = 'activity'
