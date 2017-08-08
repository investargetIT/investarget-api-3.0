# coding=utf-8
from __future__ import unicode_literals

import sys
from django.db import models

# Create your models here.
from django.db.models import Q
from django.db.models import QuerySet
from django.db.models import sql
from django.db.models.manager import BaseManager
from django.db.models.sql.where import WhereNode

from utils.customClass import MyForeignKey

reload(sys)
sys.setdefaultencoding('utf-8')


class AuditStatus(models.Model):
    '''
    审核状态
    '''
    id = models.AutoField(primary_key=True)
    nameC = models.CharField(max_length=20,blank=True,null=True)
    nameE = models.CharField(max_length=128,blank=True,null=True)
    is_deleted = models.BooleanField(blank=True, default=False)

    def __str__(self):
        return self.nameC


class ProjectStatus(models.Model):
    '''
    项目状态
    '''
    id = models.AutoField(primary_key=True)
    nameC = models.CharField(max_length=20,blank=True,null=True)
    nameE = models.CharField(max_length=128,blank=True,null=True)
    is_deleted = models.BooleanField(blank=True, default=False)

    def __str__(self):
        return self.nameC


class OrgType(models.Model):
    '''
    机构类型：投行、基金~~~
    '''
    id = models.AutoField(primary_key=True)
    nameC = models.CharField(max_length=20,blank=True,null=True)
    nameE = models.CharField(max_length=128,blank=True,null=True)
    is_deleted = models.BooleanField(blank=True, default=False)

    def __str__(self):
        return self.nameC


class FavoriteType(models.Model):
    '''
    收藏类型
    '''
    id = models.AutoField(primary_key=True)
    nameC = models.CharField(max_length=20,blank=True,null=True)
    nameE = models.CharField(max_length=128,blank=True,null=True)
    is_deleted = models.BooleanField(blank=True, default=False)

    def __str__(self):
        return self.nameC


class MessageType(models.Model):
    '''
    站内信类型
    '''
    id = models.AutoField(primary_key=True)
    nameC = models.CharField(max_length=20,blank=True,null=True)
    nameE = models.CharField(max_length=128,blank=True,null=True)
    is_deleted = models.BooleanField(blank=True, default=False)

    def __str__(self):
        return self.nameC


class ClientType(models.Model):
    '''
    用户登录端类型
    '''
    id = models.AutoField(primary_key=True)
    nameC = models.CharField(max_length=20,blank=True,null=True)
    nameE = models.CharField(max_length=128,blank=True,null=True)
    is_deleted = models.BooleanField(blank=True, default=False)

    def __str__(self):
        return self.nameC


class TitleType(models.Model):
    '''
    职位
    '''
    id = models.AutoField(primary_key=True)
    nameC = models.CharField(max_length=20,blank=True,null=True)
    nameE = models.CharField(max_length=128,blank=True,null=True)
    is_deleted = models.BooleanField(blank=True, default=False)

    def __str__(self):
        return self.nameC


class CharacterType(models.Model):
    '''
    职位
    '''
    id = models.AutoField(primary_key=True)
    characterC = models.CharField(max_length=20,blank=True,null=True)
    characterE = models.CharField(max_length=128,blank=True,null=True)
    is_deleted = models.BooleanField(blank=True, default=False)

    def __str__(self):
        return self.characterC




class Country(models.Model):
    '''
    国家
    '''
    id = models.AutoField(primary_key=True)
    parent = MyForeignKey('self', related_name='parent_location', blank=True, null=True)
    countryC = models.CharField(max_length=20,blank=True,null=True)
    countryE = models.CharField(max_length=128,blank=True,null=True)
    areaCode = models.CharField(max_length=8,blank=True,null=True)
    bucket = models.CharField(max_length=20, blank=True, default='image')
    key = models.CharField(max_length=64, blank=True, null=True)
    level = models.PositiveSmallIntegerField(blank=True,default=1)
    is_deleted = models.BooleanField(blank=True, default=False)
    datasource = models.PositiveSmallIntegerField(blank=True,default=1)

    def __str__(self):
        return self.countryC

class Service(models.Model):
    '''
    项目服务
    '''
    id = models.AutoField(primary_key=True)
    nameC = models.CharField(max_length=20,blank=True,null=True)
    nameE = models.CharField(max_length=128,blank=True,null=True)
    is_deleted = models.BooleanField(blank=True, default=False)
    def __str__(self):
        return self.nameC

class CurrencyType(models.Model):
    '''
    货币类型
    '''
    id = models.AutoField(primary_key=True)
    currencyC = models.CharField(max_length=16,blank=True,null=True)
    currencyE = models.CharField(max_length=32,blank=True,null=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.currencyC


class Industry(models.Model):
    '''
    行业
    '''
    id = models.AutoField(primary_key=True)
    isPindustry = models.BooleanField(blank=True, default=False, help_text='是否是父级行业')
    Pindustry = MyForeignKey('self', blank=True, null=True, related_name='Pindustry_Sindustries', help_text='父级行业')
    industryC = models.CharField(max_length=16,blank=True,null=True)
    industryE = models.CharField(max_length=128,blank=True,null=True)
    bucket = models.CharField(max_length=16, blank=True, default='image')
    key = models.CharField(max_length=64, blank=True, null=True)
    is_deleted = models.BooleanField(blank=True, default=False)
    datasource = models.SmallIntegerField(blank=True, default=1)
    def __str__(self):
        return self.countryC


class Tag(models.Model):
    '''
    热门标签
    '''
    id = models.AutoField(primary_key=True)
    nameC = models.CharField(max_length=20,blank=True,null=True)
    nameE = models.CharField(max_length=128,blank=True,null=True)
    hotpoint = models.SmallIntegerField(blank=True, default=0)
    datasource = models.SmallIntegerField(blank=True, default=1)
    is_deleted = models.BooleanField(blank=True, default=False)

    def __str__(self):
        return self.nameC


class OrgArea(models.Model):
    '''
    机构地区
    '''
    id = models.AutoField(primary_key=True)
    nameC = models.CharField(max_length=20,blank=True,null=True)
    nameE = models.CharField(max_length=128,blank=True,null=True)
    is_deleted = models.BooleanField(blank=True, default=False)

    def __str__(self):
        return self.nameC


class School(models.Model):
    '''
    学校
    '''
    id = models.AutoField(primary_key=True)
    nameC = models.TextField(blank=True, default='无')
    nameE = models.TextField(blank=True, default='none')
    is_deleted = models.BooleanField(blank=True, default=False)

    def __str__(self):
        return self.nameC


class Specialty(models.Model):
    '''
    专业
    '''
    id = models.AutoField(primary_key=True)
    nameC = models.TextField(blank=True, default='无')
    nameE = models.TextField(blank=True, default='none')
    is_deleted = models.BooleanField(blank=True, default=False)

    def __str__(self):
        return self.nameC


class TransactionPhases(models.Model):
    '''
    机构状态：e.天使轮，A轮，B轮~
    '''
    id = models.AutoField(primary_key=True)
    nameC = models.CharField(max_length=20,blank=True,null=True)
    nameE = models.CharField(max_length=128,blank=True,null=True)
    is_deleted = models.BooleanField(blank=True, default=False)

    def __str__(self):
        return self.nameC


class TransactionType(models.Model):
    '''
    交易类型：兼并收购、股权融资、少数股权装让~
    '''
    id = models.AutoField(primary_key=True)
    nameC = models.CharField(max_length=20,blank=True,null=True)
    nameE = models.CharField(max_length=128,blank=True,null=True)
    is_deleted = models.BooleanField(blank=True, default=False)

    def __str__(self):
        return self.nameC


class TransactionStatus(models.Model):
    '''
    项目进程（时间轴）状态：11个step
    '''
    id = models.AutoField(primary_key=True)
    nameC = models.CharField(max_length=16,blank=True,null=True)
    nameE = models.CharField(max_length=32,blank=True,null=True)
    index = models.PositiveSmallIntegerField(blank=True, default=0)
    is_deleted = models.BooleanField(blank=True, default=False)

    def __str__(self):
        return self.nameC


class DataSource(models.Model):
    '''
    平台来源（数据）
     '''
    id = models.AutoField(primary_key=True)
    nameC = models.CharField(max_length=32,blank=True,null=True)
    nameE = models.CharField(max_length=128, blank=True, null=True)
    is_deleted = models.BooleanField(blank=True, default=False)

    def __str__(self):
        return self.nameC


class webmenu(models.Model):
    """
    菜单
    """
    id = models.AutoField(primary_key=True)
    namekey = models.CharField(max_length=32, blank=True, null=True)
    icon_active = models.CharField(max_length=64, blank=True, null=True)
    icon_normal = models.CharField(max_length=64, blank=True, null=True, )
    parentmenu = MyForeignKey('self', blank=True, null=True, related_name='Pmenu_Smenus')
    index = models.SmallIntegerField(blank=True, default=1)
    is_deleted = models.BooleanField(blank=True,default=False)

class orgtitletable(models.Model):
    """
    机构职位对照表
    """
    orgtype = MyForeignKey(OrgType, blank=True, null=True)
    title = MyForeignKey(TitleType, blank=True, null=True)
    titleindex = models.PositiveSmallIntegerField(blank=True,default=0,help_text='职位权重')
    is_deleted = models.BooleanField(blank=True, default=False)



