#coding=utf-8
from __future__ import unicode_literals

import datetime
from django.contrib.contenttypes.models import ContentType
from django.db import models

# Create your models here.
from proj.models import project
from sourcetype.models import MessageType, DataSource, Country
from usersys.models import MyUser

#站内信
from utils.customClass import InvestError, MyForeignKey, MyModel


class message(MyModel):
    content = models.TextField(verbose_name='站内信详细内容',blank=True,null=True)
    type = models.IntegerField(MessageType,blank=True,default=1,help_text='消息类型')
    messagetitle = models.CharField(max_length=128,verbose_name='消息标题',blank=True,null=True)
    sender = MyForeignKey(MyUser,blank=True,null=True,related_name='usersend_msgs')
    receiver = MyForeignKey(MyUser,related_name='userreceive_msgs',blank=True,null=True)
    isRead = models.BooleanField(verbose_name='是否已读',default=False,blank=True)
    sourcetype = models.CharField(max_length=32,blank=True,null=True,help_text='资源类型')
    sourceid = models.IntegerField(blank=True,null=True,help_text='关联资源id')
    readtime = models.DateTimeField(blank=True,null=True)
    datasource = MyForeignKey(DataSource, help_text='数据源',blank=True,default=1)
    def save(self, *args, **kwargs):
        if not self.datasource:
            raise InvestError(code=8888, msg='datasource有误')
        if not self.receiver:
            raise InvestError(code=2018)
        return super(message, self).save(*args, **kwargs)
    def __str__(self):
        return self.messagetitle
    class Meta:
        db_table = 'msg'

class schedule(MyModel):
    user = MyForeignKey(MyUser,blank=True,null=True,help_text='日程对象',related_name='user_beschedule')
    scheduledtime = models.DateTimeField(blank=True,null=True,help_text='日程预定时间',)
    comments = models.TextField(blank=True, null=True, help_text='内容')
    address = models.TextField(blank=True, null=True, help_text='具体地址')
    country = MyForeignKey(Country,blank=True,null=True,help_text='地区')
    proj = MyForeignKey(project,blank=True,null=True,help_text='日程项目',related_name='proj_schedule')
    projtitle = models.CharField(max_length=128,blank=True,null=True)
    createuser = MyForeignKey(MyUser, blank=True, null=True, related_name='usercreate_schedule')
    deleteduser = MyForeignKey(MyUser, blank=True, null=True, related_name='userdelete_schedule')
    datasource = models.IntegerField(blank=True, null=True)
    class Meta:
        db_table = 'schedule'
        permissions = (
            ('admin_manageSchedule', '管理员管理日程'),
        )

    def save(self, *args, **kwargs):
        if self.createuser is None:
            raise InvestError(2007,msg='createuser can`t be null')
        if self.scheduledtime < datetime.datetime.now():
            raise InvestError(2007,msg='日程时间不能是过去的时间')
        if self.projtitle is None:
            if self.proj:
                self.projtitle = self.proj.projtitleC
        self.datasource = self.createuser.datasource_id
        return super(schedule, self).save(*args, **kwargs)