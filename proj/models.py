#coding=utf8
from __future__ import unicode_literals

from django.db import models

# Create your models here.

from usersys.models import MyUser
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


class project(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=128)
    statu = models.IntegerField(choices=((1,'未审核'),(2,'审核完成'),(3,'未发布'),(4,'已发布'),(5,'交易中'),(6,'已完成'),(7,'已下架')),default=1)
    supportuser = models.ForeignKey(MyUser,related_name='projsupportuser')
    description = models.TextField(default='项目描述******')
    finance = models.OneToOneField('finance',null=True,blank=True,related_name='proj')
    def __str__(self):
        return self.title

class finance(models.Model):
    id = models.AutoField(primary_key=True)
    incomeFrom = models.IntegerField(default=0)
    incomeTo = models.IntegerField(default=0)
    profitFrom = models.IntegerField(default=0)
    profitTo = models.IntegerField(default=0)
    proj = models.ForeignKey(project,unique=True,blank=True,null=True)
    def __str__(self):
        try:
            proj = self.proj
            return proj.title
        except project.DoesNotExist:
            pass
        return self.id.__str__()


class favorite(models.Model):
    proj = models.ForeignKey(project)
    user = models.ForeignKey(MyUser)
    favoritetype = models.IntegerField(choices=((1,'主动收藏'),(2,'交易师推荐'),(3,'感兴趣'),(4,'平台推荐')))
    def __str__(self):
        return self.favoritetype.__str__() + self.proj.title + self.user.name

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        obj = favorite.objects.filter(proj=self.proj,user=self.user,favoritetype=self.favoritetype)
        if obj:
            raise ValueError('已经存在一条相同的记录了')
        else:
            super(favorite, self).save()

    class Meta:
        ordering = ('proj',)
