#coding=utf-8
from __future__ import unicode_literals
from django.db import models
import sys

from django.db.models import Q
from guardian.shortcuts import assign_perm, remove_perm

from sourcetype.models import AuditStatus, OrgType , TransactionPhases,CurrencyType, Industry, DataSource
from usersys.models import MyUser
from utils.customClass import InvestError

reload(sys)
sys.setdefaultencoding('utf-8')
# Create your models here.


class organization(models.Model):
    id = models.AutoField(primary_key=True)
    description = models.TextField(blank=True,null=True)
    investoverseasproject = models.BooleanField(blank=True, default=True, help_text='是否投海外项目')
    orgtransactionphase = models.ManyToManyField(TransactionPhases, through='orgTransactionPhase',through_fields=('org', 'transactionPhase'), blank=True)
    currency = models.ForeignKey(CurrencyType,blank=True,null=True,related_name='currency_orgs',on_delete=models.SET_NULL)
    decisionCycle = models.SmallIntegerField(blank=True,null=True)
    decisionMakingProcess = models.TextField(blank=True,null=True)
    nameC = models.CharField(max_length=128,blank=True,null=True)
    nameE = models.CharField(max_length=128,blank=True,null=True)
    orgcode = models.CharField(max_length=128,blank=True,null=True)
    orgtype = models.ForeignKey(OrgType,blank=True,null=True)
    transactionAmountF = models.BigIntegerField(blank=True,null=True)
    transactionAmountT = models.BigIntegerField(blank=True,null=True)
    weChat = models.CharField(max_length=32,blank=True,null=True)
    fundSize = models.BigIntegerField(blank=True,null=True)
    address = models.TextField(blank=True,null=True)
    typicalCase = models.TextField(blank=True,null=True)
    fundSize_USD = models.BigIntegerField(blank=True,null=True)
    transactionAmountF_USD = models.BigIntegerField(blank=True,null=True)
    transactionAmountT_USD = models.BigIntegerField(blank=True,null=True)
    partnerOrInvestmentCommiterMember = models.TextField(blank=True,null=True)
    mobile = models.CharField(max_length=16,blank=True,null=True)
    mobileAreaCode = models.CharField(max_length=10, blank=True, null=True, default='86',help_text='电话区号')
    industry = models.ForeignKey(Industry,help_text='机构行业',blank=True,null=True)
    webSite = models.URLField(blank=True,null=True)
    companyEmail = models.EmailField(blank=True,null=True,max_length=32)
    orgstatus = models.ForeignKey(AuditStatus, blank=True, default=1)
    auditUser = models.ForeignKey(MyUser, blank=True, null=True, related_name='useraudit_orgs')
    is_deleted = models.BooleanField(blank=True, default=False)
    deleteuser = models.ForeignKey(MyUser, blank=True, null=True,related_name='userdelete_orgs')
    deletetime = models.DateTimeField(blank=True, null=True)
    createuser = models.ForeignKey(MyUser, blank=True, null=True,related_name='usercreate_orgs')
    createtime = models.DateTimeField(auto_now_add=True,blank=True,null=True)
    lastmodifyuser = models.ForeignKey(MyUser, blank=True, null=True,related_name='usermodify_orgs')
    lastmodifytime = models.DateTimeField(auto_now=True,blank=True,null=True)
    datasource = models.ForeignKey(DataSource,help_text='数据源')
    def __str__(self):
        return self.nameC
    class Meta:
        db_table = "org"
        permissions = (
            ('admin_addorg','管理员新增机构'),
            ('admin_changeorg','管理员修改机构'),
            ('admin_deleteorg','管理员删除机构'),
            ('admin_getorg','管理员查看机构信息'),

            ('user_addorg', '用户新增机构'),
            ('user_changeorg', '用户修改机构(obj级别权限)'),
            ('user_deleteorg', '用户删除机构(obj级别权限)'),
            ('user_getorg', '用户查看机构'),
        )
    def get_transactionPhases(self):
        return self.orgtransactionphase

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.datasource:
            raise InvestError(code=8888,msg='机构datasource不能空')
        if self.pk:
            oldorg = organization.objects.get(pk=self.pk)
            if self.orgcode:
                if organization.objects.exclude(pk=self.pk).filter(is_deleted=False,orgcode=self.orgcode,datasource=self.datasource).exists():
                    raise InvestError(code=5001,msg='orgcode已存在')
            if self.is_deleted and oldorg.createuser:
                remove_perm('org.user_getorg', oldorg.createuser, self)
                remove_perm('org.user_changeorg', oldorg.createuser, self)
                remove_perm('org.user_deleteorg', oldorg.createuser, self)
        else:
            if self.orgcode:
                if organization.objects.filter(is_deleted=False,orgcode=self.orgcode,datasource=self.datasource).exists():
                    raise InvestError(code=5001,msg='orgcode已存在')
        super(organization,self).save(force_insert,force_update,using,update_fields)

class orgTransactionPhase(models.Model):
    org = models.ForeignKey(organization,null=True,blank=True,related_name='org_orgTransactionPhases')
    transactionPhase = models.ForeignKey(TransactionPhases,null=True,blank=True,related_name='transactionPhase_orgs',on_delete=models.SET_NULL)
    is_deleted = models.BooleanField(blank=True, default=False)
    deleteduser = models.ForeignKey(MyUser, blank=True, null=True, related_name='userdelete_orgTransactionPhases',on_delete=models.SET_NULL)
    deletedtime = models.DateTimeField(blank=True, null=True)
    createdtime = models.DateTimeField(auto_created=True,blank=True,null=True)
    createuser = models.ForeignKey(MyUser, blank=True, null=True, related_name='usercreate_orgTransactionPhase',on_delete=models.SET_NULL)

    class Meta:
        db_table = "org_TransactionPhase"

class orgRemarks(models.Model):
    id = models.AutoField(primary_key=True)
    org = models.ForeignKey(organization,null=True,blank=True,related_name='org_remarks')
    remark = models.TextField(blank=True,null=True)
    is_deleted = models.BooleanField(blank=True, default=False)
    deleteduser = models.ForeignKey(MyUser, blank=True, null=True, related_name='userdelete_orgremarks',on_delete=models.SET_NULL)
    deletedtime = models.DateTimeField(blank=True, null=True)
    createtime = models.DateTimeField(auto_now_add=True,blank=True,null=True)
    createuser = models.ForeignKey(MyUser, blank=True, null=True, related_name='usercreate_orgremarks',on_delete=models.SET_NULL)
    lastmodifytime = models.DateTimeField(auto_now=True,blank=True,null=True)
    lastmodifyuser = models.ForeignKey(MyUser,  blank=True, null=True,related_name='usermodify_orgremarks', related_query_name='orgremark_modifyuser',on_delete=models.SET_NULL)
    datasource = models.ForeignKey(DataSource, help_text='数据源')
    class Meta:
        db_table = "orgremark"
        permissions = (
            ('admin_getorgremark','管理员查看机构备注'),
            ('admin_changeorgremark', '管理员修改机构备注'),
            ('admin_addorgremark', '管理员增加机构备注'),
            ('admin_deleteorgremark', '管理员删除机构备注'),

            ('user_getorgremark', '用户查看机构备注（obj级别）'),
            ('user_changeorgremark', '用户修改机构备注（obj级别）'),
            ('user_addorgremark', '用户增加机构备注'),
            ('user_deleteorgremark','用户删除机构备注（obj级别）'),
        )
    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.datasource or self.datasource != self.org.datasource:
            raise InvestError(code=8888,msg='机构备注没有datasource')
        super(orgRemarks,self).save(force_insert,force_update,using,update_fields)