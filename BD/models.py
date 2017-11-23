#coding=utf8
from __future__ import unicode_literals

import datetime
from django.db import models

# Create your models here.
from org.models import organization
from proj.models import project
from sourcetype.models import Country, BDStatus
from sourcetype.models import TitleType
from usersys.models import MyUser
from usersys.views import makeUserRelation, makeUserRemark
from utils.customClass import MyForeignKey, InvestError

bd_sourcetype = (
    (0,'全库搜索'),
    (1,'其他')
)
class ProjectBD(models.Model):
    location = MyForeignKey(Country,blank=True,null=True,help_text='项目地区')
    com_name = models.TextField(blank=True,null=True,help_text='公司名称/项目名称')
    usertitle = MyForeignKey(TitleType,blank=True,null=True,help_text='职位')
    username = models.CharField(max_length=64,blank=True,null=True,help_text='姓名')
    usermobile = models.CharField(max_length=64,blank=True,null=True,help_text='电话')
    bduser = MyForeignKey(MyUser, blank=True, null=True, help_text='bd对象id')
    source = models.TextField(blank=True,null=True,help_text='来源')
    source_type = models.IntegerField(blank=True,null=True,choices=bd_sourcetype)
    manager = MyForeignKey(MyUser,blank=True,null=True,help_text='负责人',related_name='user_projBDs')
    bd_status = MyForeignKey(BDStatus,blank=True,null=True,help_text='bd状态')
    is_deleted = models.BooleanField(blank=True,default=False)
    deleteduser = MyForeignKey(MyUser, blank=True, null=True, related_name='userdelete_ProjectBD')
    deletedtime = models.DateTimeField(blank=True, null=True)
    createdtime = models.DateTimeField(auto_created=True, blank=True, null=True)
    createuser = MyForeignKey(MyUser, blank=True, null=True, related_name='usercreate_ProjectBD')
    datasource = models.IntegerField(blank=True,null=True)

    class Meta:
        permissions = (
            ('manageProjectBD', '管理项目BD'),
            ('getProjectBD', '查看项目BD'),
        )

    def save(self, *args, **kwargs):
        if self.createdtime is None:
            self.createdtime = datetime.datetime.now()
        if self.manager is None:
            raise InvestError(2007,msg='manager can`t be null')
        if self.bduser:
            self.username = self.bduser.usernameC
            self.usermobile = self.bduser.mobile
            self.usertitle = self.bduser.title.nameC
        self.datasource = self.manager.datasource_id
        if self.source == '全库搜索':
            self.source_type = 0
        else:
            self.source_type = 1
        return super(ProjectBD, self).save(*args, **kwargs)


class ProjectBDComments(models.Model):
    comments = models.TextField(blank=True, default=False, help_text='内容')
    projectBD = MyForeignKey(ProjectBD,blank=True,null=True,help_text='bd项目',related_name='ProjectBD_comments')
    is_deleted = models.BooleanField(blank=True,default=False)
    deleteduser = MyForeignKey(MyUser, blank=True, null=True, related_name='userdelete_ProjectBDComments')
    deletedtime = models.DateTimeField(blank=True, null=True)
    createdtime = models.DateTimeField(auto_created=True, blank=True, null=True)
    createuser = MyForeignKey(MyUser, blank=True, null=True, related_name='usercreate_ProjectBDComments')
    datasource = models.IntegerField(blank=True,null=True)


    def save(self, *args, **kwargs):
        if self.createdtime is None:
            self.createdtime = datetime.datetime.now()
        if self.projectBD is None:
            raise InvestError(2007,msg='projectBD can`t be null')
        self.datasource = self.projectBD.datasource
        return super(ProjectBDComments, self).save(*args, **kwargs)



class OrgBD(models.Model):
    org = MyForeignKey(organization,blank=True,null=True,help_text='BD机构')
    proj = MyForeignKey(project,blank=True,null=True,help_text='项目名称')
    usertitle = MyForeignKey(TitleType,blank=True,null=True,help_text='职位')
    username = models.CharField(max_length=64,blank=True,null=True,help_text='姓名')
    usermobile = models.CharField(max_length=64,blank=True,null=True,help_text='电话')
    bduser = MyForeignKey(MyUser,blank=True,null=True,help_text='bd对象id')
    manager = MyForeignKey(MyUser,blank=True,null=True,help_text='负责人',related_name='user_orgBDs')
    bd_status = MyForeignKey(BDStatus,blank=True,null=True,help_text='bd状态')
    is_deleted = models.BooleanField(blank=True,default=False)
    deleteduser = MyForeignKey(MyUser, blank=True, null=True, related_name='userdelete_OrgBD')
    deletedtime = models.DateTimeField(blank=True, null=True)
    createdtime = models.DateTimeField(auto_created=True, blank=True, null=True)
    createuser = MyForeignKey(MyUser, blank=True, null=True, related_name='usercreate_OrgBD')
    datasource = models.IntegerField(blank=True,null=True)

    class Meta:
        permissions = (
            ('manageOrgBD', '管理项目BD'),
            ('getOrgBD', '查看项目BD'),
        )

    def save(self, *args, **kwargs):
        if self.createdtime is None:
            self.createdtime = datetime.datetime.now()
        if self.manager is None:
            raise InvestError(2007,msg='manager can`t be null')
        if self.bduser:
            self.username = self.bduser.usernameC
            self.usermobile = self.bduser.mobile
            self.usertitle = self.bduser.title.nameC
        self.datasource = self.manager.datasource_id
        if self.pk and self.is_deleted == False:
            if self.bd_status.nameC == 'BD成功':
                makeUserRelation(self.bduser,self.manager)
                comments = self.OrgBD_comments.all().filter(is_deleted=False)
                for comment in comments:
                    makeUserRemark(self.bduser,comment,self.manager)
        return super(OrgBD, self).save(*args, **kwargs)

class OrgBDComments(models.Model):
    comments = models.TextField(blank=True, default=False, help_text='内容')
    orgBD = MyForeignKey(OrgBD,blank=True,null=True,help_text='机构BD',related_name='OrgBD_comments')
    is_deleted = models.BooleanField(blank=True,default=False)
    deleteduser = MyForeignKey(MyUser, blank=True, null=True, related_name='userdelete_OrgBDComments')
    deletedtime = models.DateTimeField(blank=True, null=True)
    createdtime = models.DateTimeField(auto_created=True, blank=True, null=True)
    createuser = MyForeignKey(MyUser, blank=True, null=True, related_name='usercreate_OrgBDComments')
    datasource = models.IntegerField(blank=True,null=True)

    def save(self, *args, **kwargs):
        if self.createdtime is None:
            self.createdtime = datetime.datetime.now()
        if self.orgBD is None:
            raise InvestError(2007,msg='orgBD can`t be null')
        self.datasource = self.orgBD.datasource
        return super(OrgBDComments, self).save(*args, **kwargs)