#coding=utf-8
from __future__ import unicode_literals

import sys
from django.db import models

# Create your models here.
reload(sys)
sys.setdefaultencoding('utf-8')


class AuditStatus(models.Model):
    '''
    审核状态
    '''
    id = models.AutoField(primary_key=True)
    nameC = models.CharField(max_length=20)
    nameE = models.CharField(max_length=128)
    is_deleted = models.BooleanField(blank=True,default=False)
    def __str__(self):
        return self.nameC

class ProjectStatus(models.Model):
    '''
    项目状态
    '''
    id = models.AutoField(primary_key=True)
    nameC = models.CharField(max_length=20)
    nameE = models.CharField(max_length=128)
    is_deleted = models.BooleanField(blank=True, default=False)
    def __str__(self):
        return self.nameC

class OrgType(models.Model):
    '''
    机构类型：投行、基金~~~
    '''
    id = models.AutoField(primary_key=True)
    nameC = models.CharField(max_length=20)
    nameE = models.CharField(max_length=128)
    is_deleted = models.BooleanField(blank=True, default=False)
    def __str__(self):
        return self.nameC

class FavoriteType(models.Model):
    '''
    收藏类型
    '''
    id = models.AutoField(primary_key=True)
    nameC = models.CharField(max_length=20)
    nameE = models.CharField(max_length=128)
    is_deleted = models.BooleanField(blank=True, default=False)
    def __str__(self):
        return self.nameC


class MessageType(models.Model):
    '''
    站内信类型
    '''
    id = models.AutoField(primary_key=True)
    nameC = models.CharField(max_length=20)
    nameE = models.CharField(max_length=128)
    is_deleted = models.BooleanField(blank=True, default=False)
    def __str__(self):
        return self.nameC

class ClientType(models.Model):
    '''
    用户登录端类型
    '''
    id = models.AutoField(primary_key=True)
    nameC = models.CharField(max_length=20)
    nameE = models.CharField(max_length=128)
    is_deleted = models.BooleanField(blank=True, default=False)
    def __str__(self):
        return self.nameC

class TitleType(models.Model):
    '''
    职位
    '''
    id = models.AutoField(primary_key=True)
    nameC = models.CharField(max_length=20)
    nameE = models.CharField(max_length=128)
    is_deleted = models.BooleanField(blank=True, default=False)
    def __str__(self):
        return self.nameC


class Continent(models.Model):
    '''
    大洲
    '''
    id = models.AutoField(primary_key=True)
    continentC = models.CharField(max_length=20)
    continentE = models.CharField(max_length=128)
    is_deleted = models.BooleanField(blank=True, default=False)
    def __str__(self):
        return self.continentC

class Country(models.Model):
    '''
    国家
    '''
    id = models.AutoField(primary_key=True)
    continent = models.ForeignKey(Continent,related_name='countries',related_query_name='continent',blank=True,null=True)
    countryC = models.CharField(max_length=20)
    countryE = models.CharField(max_length=128)
    areaCode = models.CharField(max_length=8)
    bucket = models.CharField(max_length=20,blank=True,default='image')
    key = models.CharField(max_length=64,blank=True,null=True)
    is_deleted = models.BooleanField(blank=True, default=False)
    def __str__(self):
        return self.countryC

class CurrencyType(models.Model):
    '''
    货币类型
    '''
    id = models.AutoField(primary_key=True)
    currencyC = models.CharField(max_length=16)
    currencyE = models.CharField(max_length=16)
    is_deleted = models.BooleanField(blank=True, default=False)
    def __str__(self):
        return self.currencyC


class Industry(models.Model):
    '''
    行业
    '''
    id = models.AutoField(primary_key=True)
    isPindustry = models.BooleanField(blank=True,default=False,help_text='是否是父级行业')
    Pindustry = models.ForeignKey('self',blank=True,null=True,related_name='Pindustry_Sindustries',help_text='父级行业')
    industryC = models.CharField(max_length=16)
    industryE = models.CharField(max_length=128)
    bucket = models.CharField(max_length=16,blank=True,default='image')
    key = models.CharField(max_length=64,blank=True,null=True)
    is_deleted = models.BooleanField(blank=True, default=False)
    def __str__(self):
        return self.countryC


class Tag(models.Model):
    '''
    热门标签
    '''
    id = models.AutoField(primary_key=True)
    nameC = models.CharField(max_length=20)
    nameE = models.CharField(max_length=128)
    hotpoint = models.SmallIntegerField(blank=True,default=0)
    is_deleted = models.BooleanField(blank=True, default=False)
    def __str__(self):
        return self.nameC


class OrgArea(models.Model):
    '''
    机构地区
    '''
    id = models.AutoField(primary_key=True)
    nameC = models.CharField(max_length=20)
    nameE = models.CharField(max_length=128)
    is_deleted = models.BooleanField(blank=True, default=False)
    def __str__(self):
        return self.nameC


class School(models.Model):
    '''
    学校
    '''
    id = models.AutoField(primary_key=True)
    nameC = models.TextField(blank=True,default='无')
    nameE = models.TextField(blank=True,default='none')
    is_deleted = models.BooleanField(blank=True, default=False)
    def __str__(self):
        return self.nameC


class Specialty(models.Model):
    '''
    专业
    '''
    id = models.AutoField(primary_key=True)
    nameC = models.TextField(blank=True,default='无')
    nameE = models.TextField(blank=True,default='none')
    is_deleted = models.BooleanField(blank=True, default=False)
    def __str__(self):
        return self.nameC

class TransactionPhases(models.Model):
    '''
    机构状态：e.天使轮，A轮，B轮~
    '''
    id = models.AutoField(primary_key=True)
    nameC = models.CharField(max_length=20)
    nameE = models.CharField(max_length=128)
    is_deleted = models.BooleanField(blank=True, default=False)
    def __str__(self):
        return self.nameC

class TransactionType(models.Model):
    '''
    交易类型：兼并收购、股权融资、少数股权装让~
    '''
    id = models.AutoField(primary_key=True)
    nameC = models.CharField(max_length=20)
    nameE = models.CharField(max_length=128)
    is_deleted = models.BooleanField(blank=True, default=False)
    def __str__(self):
        return self.nameC

class TransactionStatus(models.Model):
    '''
    项目进程（时间轴）状态：11个step
    '''
    id = models.AutoField(primary_key=True)
    nameC = models.CharField(max_length=16)
    nameE = models.CharField(max_length=32)
    index = models.PositiveSmallIntegerField(blank=True,default=0)
    is_deleted = models.BooleanField(blank=True, default=False)
    def __str__(self):
        return self.nameC

class DataSource(models.Model):
    '''
    平台来源（数据）
     '''
    id = models.AutoField(primary_key=True)
    nameC = models.CharField(max_length=32)
    nameE = models.CharField(max_length=128,blank=True,null=True)
    is_deleted = models.BooleanField(blank=True, default=False)
    def __str__(self):
        return self.nameC

class webmenu(models.Model):
    """
    菜单
    """
    id = models.AutoField(primary_key=True)
    namekey = models.CharField(max_length=32,blank=True,null=True)
    uri = models.CharField(max_length=200,blank=True,null=True)
    icon = models.CharField(max_length=64,blank=True,null=True,help_text='图标链接')
    parentmenu = models.ForeignKey('self',blank=True,null=True)
    # class Meta:
    #     permissions = (
    #         # ('orgmanage','显示机构管理菜单'),
    #         # ('emailmanage','显示邮件管理菜单'),
    #         # ('timelinemanage','显示时间轴管理菜单'),
    #         # ('usermanage','显示会员管理菜单'),
    #         # ('dataroommanage','显示dataroom管理菜单'),
    #         # ('myinvestor','显示我的投资人菜单'),
    #         # ('mytrader','显示我的交易师菜单'),
    #         # ('msgcenter','显示消息中心菜单'),
    #         # ('usercenter','显示个人中心菜单'),
    #         # ('changepwd','显示修改密码菜单'),
    #         # ('personalinfo','显示个人信息菜单'),
    #         # ('logcheck','显示日志查询菜单'),
    #         # ('projmanage','显示项目管理菜单'),
    #         # ('postproj', '显示发布项目菜单'),
    #         # ('projlist', '显示平台项目菜单'),
    #         # ('groupmanage','显示group管理菜单'),
    #     )
