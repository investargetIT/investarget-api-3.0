#coding=utf-8
from __future__ import unicode_literals
from django.db import models
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
# Create your models here.


class organization(models.Model):
    name = models.CharField(max_length=128)
    orgcode = models.CharField(max_length=128,unique=True)
    orgstatu = models.IntegerField(choices=((1,'未审核'),(2,'审核通过'),(3,'审核退回')),default=1)
    orgdescription = models.TextField(blank=True,null=True)

    def __str__(self):
        return self.name