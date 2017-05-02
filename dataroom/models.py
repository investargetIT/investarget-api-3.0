#coding=utf-8
from __future__ import unicode_literals

from django.db import models

# Create your models here.
from proj.models import project
from sourcetype.models import DataSource
from usersys.models import MyUser


class dataroom(models.Model):
    id = models.AutoField(primary_key=True)
    proj = models.ForeignKey(project,related_name='proj_datarooms',help_text='dataroom关联项目')
    user = models.ForeignKey(MyUser,blank=True,null=True,related_name='user_datarooms',help_text='dataroom的用户')
    trader = models.ForeignKey(MyUser, blank=True, null=True, related_name='trader_datarooms',help_text='dataroom关联的交易师')
    investor = models.ForeignKey(MyUser, blank=True, null=True, related_name='investor_datarooms',help_text='dataroom关联的投资人')
    supportor = models.ForeignKey(MyUser, blank=True, null=True, related_name='supportor_datarooms', help_text='dataroom关联的项目方')
    isPublic = models.BooleanField(help_text='是否是公共文件夹',blank=True,default=False)
    isClose = models.BooleanField(help_text='是否关闭',blank=True,default=False)
    closeDate = models.DateTimeField(blank=True,null=True,help_text='关闭日期')
    is_deleted = models.BooleanField(blank=True, default=False)
    deleteduser = models.ForeignKey(MyUser, blank=True, null=True, related_name='userdelete_datarooms')
    deletedtime = models.DateTimeField(blank=True, null=True)
    createdtime = models.DateTimeField(auto_now_add=True)
    createuser = models.ForeignKey(MyUser, blank=True, null=True, related_name='usercreate_datarooms')
    lastmodifytime = models.DateTimeField(blank=True,null=True)
    lastmodifyuser = models.ForeignKey(MyUser, blank=True, null=True, related_name='usermodify_datarooms')
    datasource = models.ForeignKey(DataSource, help_text='数据源')
    class Meta:
        db_table = 'dataroom'
        permissions = (
            ('admin_getdataroom','管理员查看dataroom'),
            ('admin_changedataroom', '管理员修改dataroom'),
            ('admin_deletedataroom', '管理员删除dataroom'),
            ('admin_adddataroom', '管理员添加dataroom'),

            # ('user_getdataroom','用户查看dataroom(obj级别)'),
        )

class dataroomdirectory(models.Model):
    id = models.AutoField(primary_key=True)
    dataroom = models.ForeignKey(dataroom,related_name='dataroom_directories',help_text='目录或文件所属dataroom')
    parent = models.ForeignKey('self',related_name='directory_directories',help_text='目录或文件所属目录id')
    orderNO = models.SmallIntegerField(help_text='目录或文件在所属目录下的排序位置')
    isShadow = models.BooleanField(blank=True,default=False)
    shadowdirectory = models.ForeignKey('self',related_name='shadowdirectory_directory',blank=True,null=True,)
    size = models.IntegerField(blank=True,null=True,help_text='文件大小')
    filename = models.CharField(max_length=128,blank=True,null=True,help_text='文件名')
    key = models.CharField(max_length=16,blank=True,null=True,help_text='文件路径')
    bucket = models.CharField(max_length=128,blank=True,null=True,help_text='文件所在空间')
    isRead = models.BooleanField(blank=True,default=False)
    is_deleted = models.BooleanField(blank=True, default=False)
    deleteduser = models.ForeignKey(MyUser, blank=True, null=True, related_name='userdelete_dataroomdirectories')
    deletedtime = models.DateTimeField(blank=True, null=True)
    createdtime = models.DateTimeField(auto_now_add=True)
    createuser = models.ForeignKey(MyUser, blank=True, null=True, related_name='usercreate_dataroomdirectories')
    lastmodifytime = models.DateTimeField(blank=True,null=True)
    lastmodifyuser = models.ForeignKey(MyUser, blank=True, null=True, related_name='usermodify_dataroomdirectories')
    datasource = models.ForeignKey(DataSource, help_text='数据源')
    class Meta:
        db_table = 'dataroomdirectory'
        permissions = (
            # ('admin_getdataroomdirectory','管理员查看dataroom'),
            # ('admin_changedataroomdirectory', '管理员修改dataroom'),
            # ('admin_deletedataroomdirectory', '管理员删除dataroom'),
            # ('admin_adddataroomdirectory', '管理员添加dataroom'),

            # ('user_getdataroom','用户查看dataroom(obj级别)'),
        )

