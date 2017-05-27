#coding=utf-8
from __future__ import unicode_literals

from django.db import models

# Create your models here.
from sourcetype.models import MessageType, DataSource
from usersys.models import MyUser

#站内信
from utils.customClass import InvestError


class message(models.Model):
    content = models.TextField(verbose_name='站内信详细内容')
    type = models.IntegerField(MessageType,default=1)
    messagetitle = models.CharField(max_length=128,verbose_name='消息标题')
    sender = models.ForeignKey(MyUser,blank=True,null=True,related_name='usersend_msgs')
    receiver = models.ForeignKey(MyUser,related_name='userreceive_msgs')
    created = models.DateTimeField(verbose_name='创建日期',auto_now_add=True)
    isread = models.BooleanField(verbose_name='是否已读',default=False,blank=True)
    is_deleted = models.ForeignKey(MyUser,blank=True,null=True,related_name='userdelete_messages')
    datasource = models.ForeignKey(DataSource, help_text='数据源')
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