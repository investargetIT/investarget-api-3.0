#coding=utf-8
from __future__ import unicode_literals

from django.db import models

# Create your models here.
from proj.models import project
from sourcetype.models import DataSource
from usersys.models import MyUser
from utils.myClass import InvestError


class publicdirectorytemplate(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64,blank=True,null=True)
    parent = models.ForeignKey('self',blank=True,null=True)
    orderNO = models.PositiveSmallIntegerField()
    is_deleted = models.BooleanField(blank=True, default=False)
    deleteduser = models.ForeignKey(MyUser, blank=True, null=True, related_name='userdelete_publicdirectorytemplate')
    deletedtime = models.DateTimeField(blank=True, null=True)
    createdtime = models.DateTimeField(auto_now_add=True)
    createuser = models.ForeignKey(MyUser, blank=True, null=True, related_name='usercreate_publicdirectorytemplate')
    lastmodifytime = models.DateTimeField(blank=True, null=True)
    lastmodifyuser = models.ForeignKey(MyUser, blank=True, null=True, related_name='usermodify_publicdirectorytemplate')
    datasource = models.ForeignKey(DataSource, help_text='数据源')
    class Meta:
        db_table = 'dataroompublicdirectorytemplate'
        permissions = (
            # ('admin_getdataroomtemplate','管理员查看dataroomtemplate'),
            # ('admin_changedataroomtemplate', '管理员修改dataroomtemplate'),
            # ('admin_deletedataroomtemplate', '管理员删除dataroomtemplate'),
            # ('admin_adddataroomtemplate', '管理员添加dataroomtemplate'),

        )

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
            ('admin_changedataroom', '管理员修改dataroom里的文件'),
            ('admin_deletedataroom', '管理员删除dataroom'),
            ('admin_adddataroom', '管理员添加dataroom'),
            ('admin_closedataroom', '管理员关闭dataroom'),

            ('user_closedataroom', '用户关闭dataroom(obj级别)'),
            ('user_getdataroom','用户查看dataroom内的文件内容(obj级别)'), #obj级别权限针对dataroom内的文件内容
            ('user_changedataroom', '用户修改dataroom内的文件内容(obj级别)'),
            ('user_adddataroom', '用户添加dataroom(obj/class级别)'),#obj级别权限针对 添加dataroom内的文件 / class级别针对能否新建dataroom
            ('user_deletedataroom', '用户删除dataroom内的文件内容(obj/class级别)'),#obj级别权限针对dataroom 内的文件内容 / class级别针对能否删除dataroom
        )

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.proj or not self.supportor:
            raise InvestError(code=7004,msg='proj缺失或proj.supportor缺失')
        if self.supportor == self.investor or self.supportor == self.trader:
            raise InvestError(code=7003)

        super(dataroom, self).save(force_insert, force_update, using, update_fields)

class dataroomdirectoryorfile(models.Model):
    id = models.AutoField(primary_key=True)
    dataroom = models.ForeignKey(dataroom,related_name='dataroom_directories',help_text='目录或文件所属dataroom')
    parent = models.ForeignKey('self',blank=True,null=True,related_name='asparent_directories',help_text='目录或文件所属目录id')
    orderNO = models.PositiveSmallIntegerField(help_text='目录或文件在所属目录下的排序位置')
    isShadow = models.BooleanField(blank=True,default=False)
    shadowdirectory = models.ForeignKey('self',related_name='shadowdirectory_directory',blank=True,null=True,)
    size = models.IntegerField(blank=True,null=True,help_text='文件大小')
    name = models.CharField(max_length=128,blank=True,null=True,help_text='文件名或目录名')
    key = models.CharField(max_length=16,blank=True,null=True,help_text='文件路径')
    bucket = models.CharField(max_length=128,blank=True,null=True,help_text='文件所在空间')
    isFile = models.BooleanField(blank=True,default=False,help_text='true/文件，false/目录')
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
        db_table = 'dataroomdirectoryorfile'

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if (not self.parent and self.isShadow) or self.shadowdirectory == self.parent:
            raise InvestError(code=7005)


        super(dataroomdirectoryorfile, self).save(force_insert, force_update, using, update_fields)

    def checkDirectoryHasFile(self):
        if self.is_deleted:
            raise InvestError(code=7002)
        if self.isFile:
            raise True
        else:
            filequery = self.asparent_directories.filter(is_deleted=False)
            if filequery.count():
                res = False
                for fileordirectoriey in filequery:
                   res = fileordirectoriey.checkDirectoryHasFile()
                   if res:
                       break
                return res
            else:
                return False