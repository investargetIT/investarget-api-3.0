#coding=utf-8
from __future__ import unicode_literals
from django.db import models
import sys

from django.db.models import Q

from sourcetype.models import AuditStatus, OrgType , TransactionPhases,CurrencyType, Industry
from usersys.models import MyUser

reload(sys)
sys.setdefaultencoding('utf-8')
# Create your models here.


class organization(models.Model):
    id = models.AutoField(primary_key=True)
    description = models.TextField(blank=True,null=True)
    investoverseasproject = models.BooleanField(blank=True, default=True, help_text='是否投海外项目')
    orgtransactionphase = models.ManyToManyField(TransactionPhases, through='orgTransactionPhase',through_fields=('org', 'transactionPhase'), blank=True)
    currency = models.ForeignKey(CurrencyType,blank=True,null=True,related_name='currency_orgs',on_delete=models.SET_NULL)
    decisionCycle = models.SmallIntegerField(default=180)
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
    auditStatu = models.ForeignKey(AuditStatus, default=1)
    auditUser = models.ForeignKey(MyUser, blank=True, null=True, related_name='useraudit_orgs')
    is_deleted = models.BooleanField(blank=True, default=False)
    deleteuser = models.ForeignKey(MyUser, blank=True, null=True,related_name='userdelete_orgs')
    deleteuime = models.DateTimeField(blank=True, null=True)
    createuser = models.ForeignKey(MyUser, blank=True, null=True,related_name='usercreate_orgs')
    createtime = models.DateTimeField(auto_now_add=True)
    lastmodifyuser = models.ForeignKey(MyUser, blank=True, null=True,related_name='usermodify_orgs')
    lastmodifytime = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.nameC
    class Meta:
        permissions = (
            ('adminadd_org','管理员新增机构'),
            ('adminchange_org','管理员修改机构'),
            ('admindelete_org','管理员删除机构'),
            ('get_organization','查看机构信息'),
        )
    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.pk:
            if self.orgcode:
                if MyUser.objects.filter(is_deleted=False,orgcode=self.orgcode).exists():
                    raise ValueError()
        super(organization,self).save(force_insert,force_update,using,update_fields)

class orgTransactionPhase(models.Model):
    org = models.ForeignKey(organization,null=True,blank=True,related_name='transactionPhase_orgs')
    transactionPhase = models.ForeignKey(TransactionPhases,null=True,blank=True,related_name='org_orgTransactionPhases',on_delete=models.SET_NULL)
    is_deleted = models.BooleanField(blank=True, default=False)
    deleteduser = models.ForeignKey(MyUser, blank=True, null=True, related_name='userdelete_orgTransactionPhases',on_delete=models.SET_NULL)
    deletedtime = models.DateTimeField(blank=True, null=True)
    createdtime = models.DateTimeField(auto_created=True)
    createuser = models.ForeignKey(MyUser, blank=True, null=True, related_name='usercreate_orgTransactionPhase',on_delete=models.SET_NULL)

    class Meta:
        db_table = "org_TransactionPhase"
class orgRemarks(models.Model):
    id = models.AutoField(primary_key=True)
    org = models.ForeignKey(organization,null=True,blank=True,on_delete=models.SET_NULL)
    remark = models.TextField(blank=True,null=True)
    is_deleted = models.BooleanField(blank=True, default=False)
    deleteduser = models.ForeignKey(MyUser, blank=True, null=True, related_name='userdelete_orgremarks',on_delete=models.SET_NULL)
    deletedtime = models.DateTimeField(blank=True, null=True)
    createdtime = models.DateTimeField(auto_created=True)
    createuser = models.ForeignKey(MyUser, blank=True, null=True, related_name='usercreate_orgremarks',on_delete=models.SET_NULL)
    lastmodifytime = models.DateTimeField(auto_now=True)
    lastmodifyuser = models.ForeignKey(MyUser,  blank=True, null=True,related_name='usermodify_orgremarks', related_query_name='orgremark_modifyuser',on_delete=models.SET_NULL)

    class Meta:
        db_table = "orgremark"