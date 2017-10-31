#coding=utf-8
from __future__ import unicode_literals

from django.db import models

# Create your models here.
from proj.models import project
from sourcetype.models import DataSource
from usersys.models import MyUser
from utils.customClass import InvestError, MyForeignKey
from utils.util import add_perm, rem_perm


class publicdirectorytemplate(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64,blank=True,null=True)
    parent = MyForeignKey('self',blank=True,null=True)
    orderNO = models.PositiveSmallIntegerField()
    is_deleted = models.BooleanField(blank=True, default=False)
    deleteduser = MyForeignKey(MyUser, blank=True, null=True, related_name='userdelete_publicdirectorytemplate')
    deletedtime = models.DateTimeField(blank=True, null=True)
    createdtime = models.DateTimeField(auto_now_add=True, null=True)
    createuser = MyForeignKey(MyUser, blank=True, null=True, related_name='usercreate_publicdirectorytemplate')
    lastmodifytime = models.DateTimeField(blank=True, null=True)
    lastmodifyuser = MyForeignKey(MyUser, blank=True, null=True, related_name='usermodify_publicdirectorytemplate')
    class Meta:
        db_table = 'dataroompublicdirectorytemplate'

class dataroom(models.Model):
    id = models.AutoField(primary_key=True)
    proj = MyForeignKey(project,related_name='proj_datarooms',help_text='dataroom关联项目')
    isClose = models.BooleanField(help_text='是否关闭',blank=True,default=False)
    closeDate = models.DateTimeField(blank=True,null=True,help_text='关闭日期')
    is_deleted = models.BooleanField(blank=True, default=False)
    deleteduser = MyForeignKey(MyUser, blank=True, null=True, related_name='userdelete_datarooms')
    deletedtime = models.DateTimeField(blank=True, null=True)
    createdtime = models.DateTimeField(blank=True, null=True,auto_now_add=True)
    createuser = MyForeignKey(MyUser, blank=True, null=True, related_name='usercreate_datarooms')
    lastmodifytime = models.DateTimeField(blank=True,null=True)
    lastmodifyuser = MyForeignKey(MyUser, blank=True, null=True, related_name='usermodify_datarooms')
    datasource = MyForeignKey(DataSource, blank=True, null=True, help_text='数据源')
    class Meta:
        db_table = 'dataroom'
        permissions = (
            ('admin_getdataroom','管理员查看dataroom'),
            ('admin_changedataroom', '管理员修改dataroom里的文件/控制用户可见文件范围'),
            ('admin_deletedataroom', '管理员删除dataroom'),
            ('admin_adddataroom', '管理员添加dataroom'),
            ('admin_closedataroom', '管理员关闭dataroom'),
        )

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.proj:
            raise InvestError(code=7004,msg='proj缺失')
        if self.proj.projstatus_id < 4:
            # raise InvestError(5003,msg='项目尚未终审发布')
            self.proj.projstatus_id = 4
            self.proj.save()
        super(dataroom, self).save(force_insert, force_update, using, update_fields)

class dataroomdirectoryorfile(models.Model):
    id = models.AutoField(primary_key=True)
    dataroom = MyForeignKey(dataroom,related_name='dataroom_directories',help_text='目录或文件所属dataroom')
    parent = MyForeignKey('self',blank=True,null=True,related_name='asparent_directories',help_text='目录或文件所属目录id')
    orderNO = models.PositiveSmallIntegerField(help_text='目录或文件在所属目录下的排序位置',blank=True,default=0)
    size = models.IntegerField(blank=True,null=True,help_text='文件大小')
    filename = models.CharField(max_length=128,blank=True,null=True,help_text='文件名或目录名')
    key = models.CharField(max_length=128,blank=True,null=True,help_text='文件路径')
    bucket = models.CharField(max_length=128,blank=True,default='file',help_text='文件所在空间')
    isFile = models.BooleanField(blank=True,default=False,help_text='true/文件，false/目录')
    is_deleted = models.BooleanField(blank=True, default=False)
    deleteduser = MyForeignKey(MyUser, blank=True, null=True, related_name='userdelete_dataroomdirectories')
    deletedtime = models.DateTimeField(blank=True, null=True)
    createdtime = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    createuser = MyForeignKey(MyUser, blank=True, null=True, related_name='usercreate_dataroomdirectories')
    lastmodifytime = models.DateTimeField(blank=True,null=True)
    lastmodifyuser = MyForeignKey(MyUser, blank=True, null=True, related_name='usermodify_dataroomdirectories')
    datasource = MyForeignKey(DataSource, blank=True, null=True, help_text='数据源')
    class Meta:
        db_table = 'dataroomdirectoryorfile'

    def save(self, force_insert=False, force_update=False, using=None,update_fields=None):
        if self.isFile:
            try:
                if self.pk:
                    dataroomdirectoryorfile.objects.exclude(pk=self.pk).get(is_deleted=False, key=self.key)
                else:
                    dataroomdirectoryorfile.objects.get(is_deleted=False, key=self.key)
            except dataroomdirectoryorfile.DoesNotExist:
                pass
            else:
                raise InvestError(code=2004)
        if self.pk is None:
            if self.dataroom.isClose or self.dataroom.is_deleted:
                raise InvestError(7012, msg='dataroom已关闭/删除，无法添加文件/目录')
        super(dataroomdirectoryorfile, self).save(force_insert, force_update, using, update_fields)

    def checkDirectoryHasFile(self):
        if self.is_deleted:
            raise InvestError(code=7002)
        if self.isFile:
            return True
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

class dataroom_User_file(models.Model):
    dataroom = MyForeignKey(dataroom, blank=True, null=True, related_name='dataroom_users')
    user = MyForeignKey(MyUser, blank=True, null=True, related_name='user_datatooms')
    files = models.ManyToManyField(dataroomdirectoryorfile, blank=True)
    is_deleted = models.BooleanField(blank=True, default=False)
    deleteduser = MyForeignKey(MyUser, blank=True, null=True, related_name='userdelete_userdatarooms')
    deletedtime = models.DateTimeField(blank=True, null=True)
    createdtime = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    createuser = MyForeignKey(MyUser, blank=True, null=True, related_name='usercreate_userdatarooms')
    datasource = MyForeignKey(DataSource, blank=True, null=True, help_text='数据源')

    class Meta:
        db_table = 'dataroom_user'

    def save(self, force_insert=False, force_update=False, using=None,update_fields=None):
        if self.pk is None:
            if self.dataroom.isClose or self.dataroom.is_deleted:
                raise InvestError(7012,msg='dataroom已关闭/删除，无法添加用户')
            try:
                dataroom_User_file.objects.get(is_deleted=False, user=self.user, dataroom=self.dataroom)
            except dataroom_User_file.DoesNotExist:
                pass
            else:
                raise InvestError(code=2004, msg='用户已存在一个相同项目的dataroom了')
        super(dataroom_User_file, self).save(force_insert, force_update, using, update_fields)