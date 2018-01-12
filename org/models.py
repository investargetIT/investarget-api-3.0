#coding=utf-8
from __future__ import unicode_literals

from django.db import models
import sys
from guardian.shortcuts import assign_perm, remove_perm
from sourcetype.models import AuditStatus, OrgType , TransactionPhases,CurrencyType, Industry, DataSource, OrgAttribute
from usersys.models import MyUser
from utils.customClass import InvestError, MyForeignKey, MyModel

reload(sys)
sys.setdefaultencoding('utf-8')
# Create your models here.

class organization(MyModel):
    id = models.AutoField(primary_key=True)
    orglevel = models.PositiveSmallIntegerField(blank=True, default=0, help_text='机构服务级别')
    description = models.TextField(blank=True,null=True)
    investoverseasproject = models.BooleanField(blank=True, default=True, help_text='是否投海外项目')
    orgtransactionphase = models.ManyToManyField(TransactionPhases, through='orgTransactionPhase',through_fields=('org','transactionPhase'), blank=True)
    currency = MyForeignKey(CurrencyType,blank=True,default=1)
    decisionCycle = models.SmallIntegerField(blank=True,null=True)
    decisionMakingProcess = models.TextField(blank=True,null=True)
    orgnameC = models.CharField(max_length=128,blank=True,null=True)
    orgnameE = models.CharField(max_length=128,blank=True,null=True)
    stockcode = models.CharField(max_length=128,blank=True,null=True,help_text='证券代码')
    stockshortname = models.CharField(max_length=128,blank=True,null=True,help_text='证券简称')
    managerName = models.CharField(max_length=128,blank=True,null=True,help_text='基金管理人名称')
    IPOdate = models.DateTimeField(blank=True,null=True,help_text='上市日期')
    marketvalue = models.BigIntegerField(blank=True,null=True,help_text='总市值')
    orgattribute = MyForeignKey(OrgAttribute,blank=True,null=True,help_text='机构属性（国有、民营、地方、中央）')
    businessscope = models.TextField(blank=True,null=True,help_text='经营范围')
    mainproductname = models.TextField(blank=True,null=True,help_text='主营产品名称')
    mainproducttype = models.TextField(blank=True,null=True,help_text='主营产品类别')
    totalemployees = models.IntegerField(blank=True,null=True,help_text='员工总数')
    address = models.TextField(blank=True, null=True)
    orgtype = MyForeignKey(OrgType,blank=True,null=True,help_text='机构类型（基金、证券、上市公司）')
    transactionAmountF = models.BigIntegerField(blank=True,null=True)
    transactionAmountT = models.BigIntegerField(blank=True,null=True)
    weChat = models.CharField(max_length=32,blank=True,null=True)
    fundSize = models.BigIntegerField(blank=True,null=True)
    typicalCase = models.TextField(blank=True,null=True)
    fundSize_USD = models.BigIntegerField(blank=True,null=True)
    transactionAmountF_USD = models.BigIntegerField(blank=True,null=True)
    transactionAmountT_USD = models.BigIntegerField(blank=True,null=True)
    partnerOrInvestmentCommiterMember = models.TextField(blank=True,null=True)
    mobile = models.CharField(max_length=100,blank=True,null=True)
    mobileAreaCode = models.CharField(max_length=10, blank=True, null=True, default='86',help_text='电话区号')
    industry = MyForeignKey(Industry,help_text='机构行业',blank=True,null=True)
    webSite = models.CharField(max_length=128,blank=True,null=True)
    companyEmail = models.EmailField(blank=True,null=True,max_length=50)
    orgstatus = MyForeignKey(AuditStatus, blank=True, default=1)
    auditUser = MyForeignKey(MyUser, blank=True, null=True, related_name='useraudit_orgs')
    deleteduser = MyForeignKey(MyUser, blank=True, null=True,related_name='userdelete_orgs')
    createuser = MyForeignKey(MyUser, blank=True, null=True,related_name='usercreate_orgs')
    lastmodifyuser = MyForeignKey(MyUser, blank=True, null=True,related_name='usermodify_orgs')
    datasource = MyForeignKey(DataSource,help_text='数据源')

    def __str__(self):
        return self.orgnameC
    class Meta:
        db_table = "org"
        permissions = (
            ('admin_addorg','管理员新增机构'),
            ('admin_changeorg','管理员修改机构'),
            ('admin_deleteorg','管理员删除机构'),
            ('admin_getorg','管理员查看机构信息'),

            ('user_addorg', '用户新增机构'),
            ('user_changeorg', '用户修改机构(obj级别)'),
            ('user_deleteorg', '用户删除机构(obj级别)'),
            ('user_getorg', '用户查看机构（obj级别）'),
        )

    def activeTransactionPhase(self):
        qs = self.orgtransactionphase.filter(transactionPhase_orgs__is_deleted=False)
        qs = qs.filter(is_deleted=False)
        return qs

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.datasource:
            raise InvestError(code=8888,msg='机构datasource不能空')
        if not self.orgnameC and not self.orgnameE:
            raise InvestError(2007,msg='机构名称不能为空')
        if self.orgnameC and not self.orgnameE:
            self.orgnameE = self.orgnameC
        if self.orgnameE and not self.orgnameC:
            self.orgnameC = self.orgnameE
        if self.industry:
            if self.industry.datasource != self.datasource_id:
                raise InvestError(8888)
        if self.pk:
            oldorg = organization.objects.get(pk=self.pk)
            if self.orgnameC:
                if organization.objects.exclude(pk=self.pk).filter(is_deleted=False,orgnameC=self.orgnameC,datasource=self.datasource).exists():
                    raise InvestError(code=5001,msg='同名机构已存在,无法修改')
            if self.is_deleted and oldorg.createuser:
                remove_perm('org.user_getorg', oldorg.createuser, self)
                remove_perm('org.user_changeorg', oldorg.createuser, self)
                remove_perm('org.user_deleteorg', oldorg.createuser, self)
        else:
            if self.orgnameC:
                if organization.objects.filter(is_deleted=False,orgnameC=self.orgnameC,datasource=self.datasource).exists():
                    raise InvestError(code=5001,msg='同名机构已存在，无法新增')
        super(organization,self).save(force_insert,force_update,using,update_fields)

class orgTransactionPhase(MyModel):
    org = MyForeignKey(organization,null=True,blank=True,related_name='org_orgTransactionPhases')
    transactionPhase = MyForeignKey(TransactionPhases,null=True,blank=True,related_name='transactionPhase_orgs',on_delete=models.SET_NULL)
    deleteduser = MyForeignKey(MyUser, blank=True, null=True, related_name='userdelete_orgTransactionPhases',on_delete=models.SET_NULL)
    createuser = MyForeignKey(MyUser, blank=True, null=True, related_name='usercreate_orgTransactionPhase',on_delete=models.SET_NULL)

    class Meta:
        db_table = "org_TransactionPhase"

class orgRemarks(MyModel):
    id = models.AutoField(primary_key=True)
    org = MyForeignKey(organization,null=True,blank=True,related_name='org_remarks')
    remark = models.TextField(blank=True,null=True)
    deleteduser = MyForeignKey(MyUser, blank=True, null=True, related_name='userdelete_orgremarks',on_delete=models.SET_NULL)
    createuser = MyForeignKey(MyUser, blank=True, null=True, related_name='usercreate_orgremarks',on_delete=models.SET_NULL)
    lastmodifyuser = MyForeignKey(MyUser,  blank=True, null=True,related_name='usermodify_orgremarks', related_query_name='orgremark_modifyuser',on_delete=models.SET_NULL)
    datasource = MyForeignKey(DataSource, help_text='数据源')
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