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
    user = MyForeignKey(MyUser,blank=True,null=True,related_name='user_datarooms',help_text='项目方')
    trader = MyForeignKey(MyUser, blank=True, null=True, related_name='trader_datarooms',help_text='dataroom关联的交易师')
    investor = MyForeignKey(MyUser, blank=True, null=True, related_name='investor_datarooms',help_text='dataroom关联的投资人')
    isPublic = models.BooleanField(help_text='是否是公共文件夹',blank=True,default=False)
    isClose = models.BooleanField(help_text='是否关闭',blank=True,default=False)
    closeDate = models.DateTimeField(blank=True,null=True,help_text='关闭日期')
    is_deleted = models.BooleanField(blank=True, default=False)
    deleteduser = MyForeignKey(MyUser, blank=True, null=True, related_name='userdelete_datarooms')
    deletedtime = models.DateTimeField(blank=True, null=True)
    createdtime = models.DateTimeField(blank=True, null=True,auto_now_add=True)
    createuser = MyForeignKey(MyUser, blank=True, null=True, related_name='usercreate_datarooms')
    lastmodifytime = models.DateTimeField(blank=True,null=True)
    lastmodifyuser = MyForeignKey(MyUser, blank=True, null=True, related_name='usermodify_datarooms')
    datasource = MyForeignKey(DataSource, help_text='数据源')
    class Meta:
        db_table = 'dataroom'
        permissions = (
            ('admin_getdataroom','管理员查看dataroom'),
            ('admin_changedataroom', '管理员修改dataroom里的文件'),
            ('admin_deletedataroom', '管理员删除dataroom'),
            ('admin_adddataroom', '管理员添加dataroom'),
            ('admin_closedataroom', '管理员关闭dataroom'),

            ('user_closedataroom', '用户关闭dataroom(obj级别)'),
            ('user_getdataroom','用户查看dataroom内的文件内容(obj级别)'),
            ('user_changedataroom', '用户修改dataroom内的文件内容(obj级别)'),#重命名
            ('user_adddataroomfile', '用户添加dataroom(obj级别)'),  #obj级别权限针对 添加dataroom内的文件
            ('user_adddataroom', '用户新建dataroom'),  #class级别针对能否新建dataroom
            ('user_deletedataroom', '用户删除dataroom内的文件内容(obj级别)'), #obj级别权限针对能否删除dataroom内的文件内容/能否删除dataroom
        )

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.proj:
            raise InvestError(code=7004,msg='proj缺失')
        if self.proj.projstatus_id < 4:
            raise InvestError(5003,msg='项目尚未终审发布')
        if self.proj.supportUser and self.proj.supportUser == self.investor:
            raise InvestError(7003,msg='项目上传者不能作为投资人')
        if self.trader.userstatus_id != 2 or self.investor.userstatus_id != 2:
            raise InvestError(2022)
        if self.pk:
            if self.isPublic == False and self.user is None:
                if self.is_deleted:
                    userlist = [self.investor, self.trader, self.createuser, self.proj.makeUser, self.proj.takeUser,]
                    userlist = set(userlist)
                    for user in userlist:
                        rem_perm('dataroom.user_getdataroom', user, self)
                    rem_perm('dataroom.user_changedataroom', self.investor, self)
                else:
                    oldrela = dataroom.objects.get(pk=self.pk)
                    userlist1 = [oldrela.investor, oldrela.trader, oldrela.createuser, oldrela.proj.makeUser,
                                 oldrela.proj.takeUser,]
                    userlist2 = [self.investor, self.trader, self.createuser, self.proj.makeUser, self.proj.takeUser,]
                    userset1 = set(userlist1)
                    userset2 = set(userlist2)
                    if userset1 != userset2:
                        for user in userset1:
                            rem_perm('dataroom.user_getdataroom', user, self)
                        rem_perm('dataroom.user_changedataroom', oldrela.investor, self)
                        for user in userset2:
                            add_perm('dataroom.user_getdataroom', user, self)
                        add_perm('dataroom.user_changedataroom', self.investor, self)
            elif self.isPublic == False and self.user is not None:
                if self.is_deleted:
                    userlist = [self.createuser, self.proj.makeUser, self.proj.takeUser, ]
                    userlist = set(userlist)
                    for user in userlist:
                        rem_perm('dataroom.user_getdataroom', user, self)
                    rem_perm('dataroom.user_getdataroom', self.user, self)
                    rem_perm('dataroom.user_changedataroom', self.user, self)
                else:
                    oldrela = dataroom.objects.get(pk=self.pk)
                    userlist1 = [oldrela.createuser, oldrela.proj.makeUser,oldrela.proj.takeUser, ]
                    userlist2 = [ self.createuser, self.proj.makeUser, self.proj.takeUser, ]
                    userset1 = set(userlist1)
                    userset2 = set(userlist2)
                    if userset1 != userset2:
                        for user in userset1:
                            rem_perm('dataroom.user_getdataroom', user, self)
                        rem_perm('dataroom.user_getdataroom', oldrela.user, self)
                        rem_perm('dataroom.user_changedataroom', oldrela.user, self)
                        for user in userset2:
                            add_perm('dataroom.user_getdataroom', user, self)
                        add_perm('dataroom.user_getdataroom', self.user, self)
                        add_perm('dataroom.user_changedataroom', self.user, self)
            else:
                pass
        super(dataroom, self).save(force_insert, force_update, using, update_fields)

class dataroomdirectoryorfile(models.Model):
    id = models.AutoField(primary_key=True)
    dataroom = MyForeignKey(dataroom,related_name='dataroom_directories',help_text='目录或文件所属dataroom')
    parent = MyForeignKey('self',blank=True,null=True,related_name='asparent_directories',help_text='目录或文件所属目录id')
    orderNO = models.PositiveSmallIntegerField(help_text='目录或文件在所属目录下的排序位置',blank=True,default=0)
    isShadow = models.BooleanField(blank=True,default=False)
    shadowdirectory = MyForeignKey('self',related_name='shadowdirectory_directory',blank=True,null=True,)
    size = models.IntegerField(blank=True,null=True,help_text='文件大小')
    filename = models.CharField(max_length=128,blank=True,null=True,help_text='文件名或目录名')
    key = models.CharField(max_length=128,blank=True,null=True,help_text='文件路径')
    bucket = models.CharField(max_length=128,blank=True,default='file',help_text='文件所在空间')
    isFile = models.BooleanField(blank=True,default=False,help_text='true/文件，false/目录')
    isRead = models.BooleanField(blank=True,default=False)
    is_deleted = models.BooleanField(blank=True, default=False)
    deleteduser = MyForeignKey(MyUser, blank=True, null=True, related_name='userdelete_dataroomdirectories')
    deletedtime = models.DateTimeField(blank=True, null=True)
    createdtime = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    createuser = MyForeignKey(MyUser, blank=True, null=True, related_name='usercreate_dataroomdirectories')
    lastmodifytime = models.DateTimeField(blank=True,null=True)
    lastmodifyuser = MyForeignKey(MyUser, blank=True, null=True, related_name='usermodify_dataroomdirectories')
    datasource = MyForeignKey(DataSource, help_text='数据源')
    class Meta:
        db_table = 'dataroomdirectoryorfile'

    def save(self, force_insert=False, force_update=False, using=None,update_fields=None):
        if self.pk and self.isShadow:
            if self.is_deleted:
                pass
            else:
                raise InvestError(code=7005,msg='影子目录无法操作，只能删除')
        if self.isShadow and self.shadowdirectory is None:
            raise InvestError(7005,msg='复制体必须有真身')
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
    dataroom = MyForeignKey(dataroom, blank=True, null=True)
    user = MyForeignKey(MyUser, blank=True, null=True)
    file = models.ManyToManyField(dataroomdirectoryorfile)
    is_deleted = models.BooleanField(blank=True, default=False)
    deleteduser = MyForeignKey(MyUser, blank=True, null=True, related_name='userdelete_dataroomdirectories')
    deletedtime = models.DateTimeField(blank=True, null=True)
    createdtime = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    createuser = MyForeignKey(MyUser, blank=True, null=True, related_name='usercreate_dataroomdirectories')
    datasource = MyForeignKey(DataSource, help_text='数据源')

    class Meta:
        db_table = 'dataroom_user'
