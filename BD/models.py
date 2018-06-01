#coding=utf8
from __future__ import unicode_literals

import datetime
from django.db import models

# Create your models here.
from org.models import organization
from proj.models import project
from sourcetype.models import BDStatus, OrgArea, Country, OrgBdResponse
from sourcetype.models import TitleType
from usersys.models import MyUser
from usersys.views import makeUserRemark
from utils.customClass import MyForeignKey, InvestError, MyModel

bd_sourcetype = (
    (0,'全库搜索'),
    (1,'其他')
)
class ProjectBD(MyModel):
    country = MyForeignKey(Country, blank=True, null=True, help_text='项目国家')
    location = MyForeignKey(OrgArea, blank=True, null=True, help_text='项目地区')
    com_name = models.TextField(blank=True,null=True,help_text='公司名称/项目名称')
    usertitle = MyForeignKey(TitleType,blank=True,null=True,help_text='职位')
    username = models.CharField(max_length=64,blank=True,null=True,help_text='姓名')
    usermobile = models.CharField(max_length=64,blank=True,null=True,help_text='电话')
    useremail = models.CharField(max_length=64, blank=True, null=True, help_text='邮箱')
    bduser = MyForeignKey(MyUser, blank=True, null=True, help_text='bd对象id')
    source = models.TextField(blank=True,null=True,help_text='来源')
    source_type = models.IntegerField(blank=True,null=True,choices=bd_sourcetype)
    manager = MyForeignKey(MyUser,blank=True,null=True,help_text='负责人',related_name='user_projBDs')
    bd_status = MyForeignKey(BDStatus,blank=True,null=True,help_text='bd状态')
    deleteduser = MyForeignKey(MyUser, blank=True, null=True, related_name='userdelete_ProjectBD')
    createuser = MyForeignKey(MyUser, blank=True, null=True, related_name='usercreate_ProjectBD')
    lastmodifyuser = MyForeignKey(MyUser, blank=True, null=True, related_name='usermodify_ProjectBD')
    datasource = models.IntegerField(blank=True,null=True)

    class Meta:
        permissions = (
            ('manageProjectBD', '管理员管理项目BD'),
            ('user_getProjectBD', u'用户查看个人项目BD'),
            ('user_addProjectBD', u'用户新建个人项目BD'),
            ('user_manageProjectBD', '用户管理个人项目BD（obj级别）'),
        )

    def save(self, *args, **kwargs):
        if self.manager is None:
            raise InvestError(2007,msg='manager can`t be null')
        if not self.datasource:
            raise InvestError(2007, msg='datasource can`t be null')
        if self.country:
            if self.country.datasource != self.datasource:
                raise  InvestError(8888, msg='datasource 不匹配')
        if self.bduser:
            self.username = self.bduser.usernameC
            self.usermobile = self.bduser.mobile
            self.usertitle = self.bduser.title
            self.useremail = self.bduser.email
        self.datasource = self.manager.datasource_id
        if not self.source:
            if self.source_type == 0:
                self.sourcee = '全库搜索'
        if not self.manager.onjob:
            raise InvestError(2024)
        return super(ProjectBD, self).save(*args, **kwargs)


class ProjectBDComments(MyModel):
    comments = models.TextField(blank=True, default=False, help_text='内容')
    event_date = models.DateTimeField(blank=True, null=True)
    projectBD = MyForeignKey(ProjectBD,blank=True,null=True,help_text='bd项目',related_name='ProjectBD_comments')
    deleteduser = MyForeignKey(MyUser, blank=True, null=True, related_name='userdelete_ProjectBDComments')
    createuser = MyForeignKey(MyUser, blank=True, null=True, related_name='usercreate_ProjectBDComments')
    datasource = models.IntegerField(blank=True,null=True)


    def save(self, *args, **kwargs):
        if self.projectBD is None:
            raise InvestError(2007,msg='projectBD can`t be null')
        self.datasource = self.projectBD.datasource
        if self.event_date is None:
            self.event_date = datetime.datetime.now()
        return super(ProjectBDComments, self).save(*args, **kwargs)


class OrgBD(MyModel):
    org = MyForeignKey(organization,blank=True,null=True,help_text='BD机构',related_name='org_orgBDs')
    proj = MyForeignKey(project,blank=True,null=True,help_text='项目名称',related_name='proj_orgBDs')
    usertitle = MyForeignKey(TitleType,blank=True,null=True,help_text='职位')
    username = models.CharField(max_length=64,blank=True,null=True,help_text='姓名')
    usermobile = models.CharField(max_length=64,blank=True,null=True,help_text='电话')
    bduser = MyForeignKey(MyUser,blank=True,null=True,help_text='bd对象id')
    manager = MyForeignKey(MyUser,blank=True,null=True,help_text='负责人',related_name='user_orgBDs')
    isimportant = models.BooleanField(blank=True, default=False, help_text='是否重点BD')
    bd_status = MyForeignKey(BDStatus,blank=True,null=True,help_text='bd状态')
    expirationtime = models.DateTimeField(blank=True,null=True,help_text='BD过期时间')
    response = MyForeignKey(OrgBdResponse, blank=True, null=True, related_name='OrgBD_response')
    isSolved = models.BooleanField(blank=True, default=False, help_text='BD是否已处理')
    deleteduser = MyForeignKey(MyUser, blank=True, null=True, related_name='userdelete_OrgBD')
    createuser = MyForeignKey(MyUser, blank=True, null=True, related_name='usercreate_OrgBD')
    lastmodifyuser = MyForeignKey(MyUser, blank=True, null=True, related_name='usermodify_OrgBD')
    datasource = models.IntegerField(blank=True, null=True)

    class Meta:
        permissions = (
            ('manageOrgBD', '管理机构BD'),
            ('user_getOrgBD', u'用户查看个人机构BD'),
            ('user_addOrgBD', u'用户新建机构BD'),
            ('user_manageOrgBD', '用户管理个人机构BD（obj级别）'),
        )

    def save(self, *args, **kwargs):
        if self.manager is None:
            raise InvestError(2007,msg='manager can`t be null')
        if self.bduser:
            self.username = self.bduser.usernameC
            self.usermobile = self.bduser.mobile
            self.usertitle = self.bduser.title
        self.datasource = self.manager.datasource_id
        if not self.manager.onjob:
            raise InvestError(2024)
        if self.bduser and not self.is_deleted:
            if self.pk:
                bds = OrgBD.objects.exclude(pk=self.pk).filter(is_deleted=False, proj=self.proj,
                                                               datasource=self.datasource, bduser=self.bduser, manager=self.manager)
            else:
                bds = OrgBD.objects.filter(is_deleted=False, proj=self.proj,
                                           datasource=self.datasource, bduser=self.bduser, manager=self.manager)
            if bds.exists():
                raise InvestError(5006, msg='该用户已存在一条BD记录了')
        if self.is_deleted is False:
            if self.proj:
                if self.proj.projstatus < 4:
                    raise InvestError(5003,msg='项目尚未终审发布')
        if self.pk and not self.is_deleted:
            if self.bd_status.nameC == 'BD成功':
                if self.bduser:
                    comments = self.OrgBD_comments.all().filter(is_deleted=False)
                    for comment in comments:
                        makeUserRemark(self.bduser,comment,self.manager)
        return super(OrgBD, self).save(*args, **kwargs)

class OrgBDComments(MyModel):
    comments = models.TextField(blank=True, default=False, help_text='内容')
    event_date = models.DateTimeField(blank=True, null=True)
    orgBD = MyForeignKey(OrgBD,blank=True,null=True,help_text='机构BD',related_name='OrgBD_comments')
    deleteduser = MyForeignKey(MyUser, blank=True, null=True, related_name='userdelete_OrgBDComments')
    createuser = MyForeignKey(MyUser, blank=True, null=True, related_name='usercreate_OrgBDComments')
    datasource = models.IntegerField(blank=True,null=True)

    def save(self, *args, **kwargs):

        if self.orgBD is None:
            raise InvestError(2007,msg='orgBD can`t be null')
        self.datasource = self.orgBD.datasource
        if self.event_date is None:
            self.event_date = datetime.datetime.now()
        if self.orgBD and not self.orgBD.isSolved:
            self.orgBD.isSolved = True
            self.orgBD.save(update_fields=['isSolved'])
        return super(OrgBDComments, self).save(*args, **kwargs)


class MeetingBD(MyModel):
    org = MyForeignKey(organization, blank=True, null=True, help_text='BD机构', related_name='org_meetBDs')
    proj = MyForeignKey(project, blank=True, null=True, help_text='项目名称', related_name='proj_meetBDs')
    usertitle = MyForeignKey(TitleType, blank=True, null=True, help_text='职位')
    username = models.CharField(max_length=64, blank=True, null=True, help_text='姓名')
    usermobile = models.CharField(max_length=64, blank=True, null=True, help_text='电话')
    bduser = MyForeignKey(MyUser, blank=True, null=True, help_text='bd对象id')
    manager = MyForeignKey(MyUser, blank=True, null=True, help_text='负责人', related_name='user_MeetBDs')
    comments = models.TextField(blank=True, null=True, help_text='会议纪要')
    meet_date = models.DateTimeField(blank=True, null=True, help_text='会议时间')
    title = models.TextField(blank=True, null=True, help_text='会议标题')
    attachmentbucket = models.CharField(max_length=16, blank=True, null=True, help_text='附件存储空间')
    attachment = models.CharField(max_length=64, blank=True, null=True, help_text='会议附件')
    deleteduser = MyForeignKey(MyUser, blank=True, null=True, related_name='userdelete_MeetBD')
    createuser = MyForeignKey(MyUser, blank=True, null=True, related_name='usercreate_MeetBD')
    lastmodifyuser = MyForeignKey(MyUser, blank=True, null=True, related_name='usermodify_MeetBD')
    datasource = models.IntegerField(blank=True, null=True)

    class Meta:
        permissions = (
            ('manageMeetBD', '管理会议BD'),
            ('user_getMeetBD', u'用户查看个人会议BD'),
            ('user_addMeetBD', u'用户新建个人会议BD'),
            ('user_manageMeetBD', '用户管理个人会议BD（obj级别）'),
        )

    def save(self, *args, **kwargs):
        if self.manager is None:
            raise InvestError(2007, msg='manager can`t be null')
        if not self.manager.onjob:
            raise InvestError(2024)
        if self.bduser:
            self.username = self.bduser.usernameC
            self.usermobile = self.bduser.mobile
            self.usertitle = self.bduser.title
        self.datasource = self.manager.datasource_id
        return super(MeetingBD, self).save(*args, **kwargs)