#coding=utf-8
from __future__ import unicode_literals

from django.db import models

# Create your models here.
from types.models import messageType
from usersys.models import MyUser

#站内信
class message(models.Model):
    content = models.TextField(verbose_name='站内信详细内容')
    type = models.IntegerField(messageType,default=1)
    title = models.CharField(max_length=128,verbose_name='消息标题')
    sender = models.ForeignKey(MyUser,blank=True,null=True)
    receiver = models.ForeignKey(MyUser)
    created = models.DateTimeField(verbose_name='创建日期',auto_now_add=True)
    isread = models.BooleanField(verbose_name='是否已读',default=False,blank=True)
    def save(self, *args, **kwargs):
        if self.sender is self.receiver :
            return ValueError('收信人与发信人相同')
        return super(message, self).save(*args, **kwargs)
    def __str__(self):
        return self.title
    class Meta:
        db_table = 'msg'