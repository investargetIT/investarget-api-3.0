#coding=utf-8
from __future__ import unicode_literals
from django.db import models
import sys

from sourcetype.models import AuditStatus, OrgType , TransactionPhases,CurrencyType
from usersys.models import MyUser

reload(sys)
sys.setdefaultencoding('utf-8')
# Create your models here.


class organization(models.Model):
    id = models.AutoField(primary_key=True)
    description = models.TextField(blank=True,null=True)
    orgtransactionphase = models.ManyToManyField(TransactionPhases, through='orgTransactionPhase',through_fields=('org', 'transactionPhase'), blank=True)
    currency = models.ForeignKey(CurrencyType,blank=True,null=True,related_name='currency_orgs',on_delete=models.SET_NULL)
    decisionCycle = models.SmallIntegerField(default=180)
    decisionMakingProcess = models.TextField(blank=True,null=True)
    nameC = models.CharField(max_length=128,unique=True)
    nameE = models.CharField(max_length=128,unique=True,blank=True,null=True)
    orgcode = models.CharField(max_length=128,unique=True)
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
    phone = models.CharField(max_length=16,blank=True,null=True)
    webSite = models.URLField(blank=True,null=True)
    companyEmail = models.EmailField(blank=True,null=True,max_length=32)
    auditStatu = models.ForeignKey(AuditStatus, default=1)
    auditUser = models.ForeignKey(MyUser, blank=True, null=True, related_name='useraudit_org',on_delete=models.SET_NULL)
    is_deleted = models.BooleanField(blank=True, default=False)
    deleteuser = models.ForeignKey(MyUser, blank=True, null=True, on_delete=models.SET_NULL,related_name='userdelete_orgs')
    deleteuime = models.DateTimeField(blank=True, null=True)
    createuser = models.ForeignKey(MyUser, blank=True, null=True, on_delete=models.SET_NULL,related_name='usercreate_orgs')
    createtime = models.DateTimeField(auto_now_add=True)
    lastmodifyuser = models.ForeignKey(MyUser, blank=True, null=True, on_delete=models.SET_NULL,related_name='usermodify_orgs')
    lastmodifytime = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.nameC

class orgTransactionPhase(models.Model):
    org = models.ForeignKey(organization,null=True,blank=True,related_name='org_orgTransactionPhases')
    transactionPhase = models.ForeignKey(TransactionPhases,null=True,blank=True,related_name='transactionPhase_orgTransactionPhases',on_delete=models.SET_NULL)
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