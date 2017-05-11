#coding=utf-8
from __future__ import unicode_literals

import datetime

import binascii
import os
import random

from django.db import models

# Create your models here.
class MobileAuthCode(models.Model):
    mobile = models.CharField(help_text='手机号',max_length=32)
    token = models.CharField(help_text='验证码token',max_length=32)
    code = models.CharField(help_text='验证码',max_length=32)
    createTime = models.DateTimeField(auto_now_add=True)
    def isexpired(self):
        return datetime.datetime.now() - self.createTime >=  datetime.timedelta(minutes=10 * 1)
    def __str__(self):
        return self.code
    class Meta:
        db_table = "mobileAuthCode"
    def save(self, *args, **kwargs):
        if not self.token:
            self.token = binascii.hexlify(os.urandom(16)).decode()
        if not self.code:
            self.code = self.getRandomCode()
        return super(MobileAuthCode, self).save(*args, **kwargs)
    def getRandomCode(self):
        code_list = [0,1,2,3,4,5,6,7,8,9]
        myslice = random.sample(code_list, 6)
        code = ''.join(str(i) for i in myslice)
        return code