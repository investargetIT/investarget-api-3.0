#coding=utf-8
from __future__ import unicode_literals
from django.db import models
import sys

from types.models import auditStatus, orgType , transactionPhases,currencyType
from usersys.models import MyUser

reload(sys)
sys.setdefaultencoding('utf-8')
# Create your models here.


class organization(models.Model):
    id = models.AutoField(primary_key=True)
    description = models.TextField(blank=True,null=True)
    currency = models.ForeignKey(currencyType,blank=True,null=True,related_name='currency_orgs',on_delete=models.SET_NULL)
    decisionCycle = models.SmallIntegerField(default=180)
    decisionMakingProcess = models.TextField(blank=True,null=True)
    nameC = models.CharField(max_length=128,unique=True)
    nameE = models.CharField(max_length=128,unique=True,blank=True,null=True)
    orgcode = models.CharField(max_length=128,unique=True)
    auditStatu = models.IntegerField(auditStatus,default=1)
    orgtype = models.ForeignKey(orgType,blank=True,null=True)
    transactionAmountF = models.IntegerField(blank=True,null=True)
    transactionAmountT = models.IntegerField(blank=True,null=True)
    weChat = models.CharField(max_length=32,blank=True,null=True)
    fundSize = models.IntegerField(blank=True,null=True)
    address = models.TextField(blank=True,null=True)
    typicalCase = models.TextField(blank=True,null=True)
    fundSize_USD = models.IntegerField(blank=True,null=True)
    transactionAmountF_USD = models.IntegerField(blank=True,null=True)
    transactionAmountT_USD = models.IntegerField(blank=True,null=True)
    partnerOrInvestmentCommiterMember = models.TextField(blank=True,null=True)
    phone = models.CharField(max_length=16,blank=True,null=True)
    webSite = models.URLField(blank=True,null=True)
    companyEmail = models.EmailField(blank=True,null=True,max_length=32)

    isDeleted = models.BooleanField(blank=True, default=False)
    deleteUser = models.ForeignKey(MyUser, blank=True, null=True, on_delete=models.SET_NULL,related_name='userdelete_projects')
    deleteTime = models.DateTimeField(blank=True, null=True)
    createUser = models.ForeignKey(MyUser, blank=True, null=True, on_delete=models.SET_NULL,related_name='usercreate_projects')
    createTime = models.DateTimeField(auto_now_add=True)
    lastModifyUser = models.ForeignKey(MyUser, blank=True, null=True, on_delete=models.SET_NULL,related_name='usermodify_projects')
    lastModifyTime = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.nameC
    class Meta:
        db_table = 'org'