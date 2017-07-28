#coding=utf-8
from __future__ import unicode_literals

from django.contrib.contenttypes.models import ContentType
from django.db import models

# Create your models here.
from sourcetype.models import MessageType, DataSource
from usersys.models import MyUser

#站内信
from utils.customClass import InvestError, MyForeignKey


class message(models.Model):
    content = models.TextField(verbose_name='站内信详细内容',blank=True,null=True)
    type = models.IntegerField(MessageType,blank=True,default=1)
    messagetitle = models.CharField(max_length=128,verbose_name='消息标题',blank=True,null=True)
    sender = MyForeignKey(MyUser,blank=True,null=True,related_name='usersend_msgs')
    receiver = MyForeignKey(MyUser,related_name='userreceive_msgs',blank=True,null=True)
    created = models.DateTimeField(verbose_name='创建日期',auto_now_add=True)
    isRead = models.BooleanField(verbose_name='是否已读',default=False,blank=True)
    sourcetype = MyForeignKey(ContentType,blank=True,null=True,help_text='关联资源类型')
    sourceid = models.IntegerField(blank=True,null=True,help_text='关联资源id')
    readtime = models.DateTimeField(blank=True,null=True)
    is_deleted = models.BooleanField(blank=True,default=False)
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