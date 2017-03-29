#coding=utf8
from __future__ import unicode_literals

from django.db import models

# Create your models here.
from types.models import FavoriteType, ProjectStatus,CurrencyType,Tag,Country,TransactionType,Industry
from usersys.models import MyUser
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


class project(models.Model):
    id = models.AutoField(primary_key=True)
    titleC = models.CharField(max_length=128,db_index=True,default='标题')
    titleE = models.CharField(max_length=256,blank=True,null=True)
    statu = models.ForeignKey(ProjectStatus,default=1)
    c_descriptionC = models.TextField(blank=True,default='项目描述')
    c_descriptionE = models.TextField(blank=True, default='project description')
    b_introducteC = models.TextField(blank=True, default='项目介绍')
    b_introducteE = models.TextField(blank=True, default='project introduction')
    tag = models.ManyToManyField(Tag,related_name="proj_set",related_query_name="tag_proj")
    supportUser = models.ForeignKey(MyUser,blank=True,null=True,related_name='usersupport_projs',on_delete=models.SET_NULL)
    isHidden = models.BooleanField(blank=True,default=False)
    financeAmount = models.IntegerField(blank=True,null=True)
    financeAmount_USD = models.IntegerField(blank=True,null=True)
    companyValuation = models.IntegerField(verbose_name='公司估值', blank=True, null=True)
    companyValuation_USD = models.IntegerField(verbose_name='公司估值', blank=True, null=True)
    companyYear = models.SmallIntegerField(verbose_name='公司年限', blank=True, null=True)
    financeIsPublic = models.BooleanField(blank=True, default=True)
    code = models.CharField(max_length=128, blank=True, null=True)
    projFormat = models.OneToOneField(format, null=True, blank=True)
    tags = models.ManyToManyField(tag,through='projectTags',through_fields=('proj','tag'))
    industries = models.ManyToManyField(Industry, through='projectIndustries', through_fields=('proj','industry'))
    transactionType = models.ManyToManyField(TransactionType, through='projectTransactionType', through_fields=('proj', 'transactionType'))
    currency = models.ForeignKey(CurrencyType,default=1,on_delete=models.SET_NULL,null=True)
    contactPerson = models.CharField(max_length=64,blank=True,null=True)
    phoneNumber = models.CharField(max_length=32,blank=True,null=True)
    email = models.EmailField(verbose_name='邮箱', max_length=48, db_index=True,blank=True,null=True)
    country = models.ForeignKey(Country,blank=True,null=True,db_index=True)
    isDeleted = models.BooleanField(blank=True, default=False)
    deleteUser = models.ForeignKey(MyUser, blank=True, null=True, on_delete=models.SET_NULL,related_name='userdelete_projects')
    deleteTime = models.DateTimeField(blank=True, null=True)
    createUser = models.ForeignKey(MyUser, blank=True, null=True, on_delete=models.SET_NULL,related_name='usercreate_projects')
    createTime = models.DateTimeField(auto_now_add=True)
    lastModifyUser = models.ForeignKey(MyUser, blank=True, null=True, on_delete=models.SET_NULL,related_name='usermodify_projects')
    lastModifyTime = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.titleC
    class Meta:
        db_table = 'project'

class format(models.Model):
    id = models.AutoField(primary_key=True)
    targetMarketC = models.TextField(blank=True,null=True)
    targetMarketE = models.TextField(blank=True,null=True)
    productTechnologyC = models.TextField(blank=True,null=True)
    productTechnologyE = models.TextField(blank=True,null=True)
    businessModelC = models.TextField(blank=True,null=True)
    businessModelE = models.TextField(blank=True,null=True)
    brandSalesChannelC = models.TextField(blank=True,null=True)
    brandSalesChannelE = models.TextField(null=True,blank=True)
    managementC = models.TextField(blank=True,null=True)
    managementE = models.TextField(blank=True,null=True)
    partnersC = models.TextField(null=True,blank=True)
    partnersE = models.TextField(null=True,blank=True)
    useOfProceedC = models.TextField(blank=True,null=True)
    useOfProceedE = models.TextField(blank=True,null=True)
    financingRecordC = models.TextField(blank=True,null=True)
    financingRecordE = models.TextField(blank=True,null=True)
    operatingFiguresC = models.TextField(blank=True,null=True)
    operatingFiguresE = models.TextField(blank=True,null=True)
    isDeleted = models.BooleanField(blank=True,default=False)
    deleteUser = models.ForeignKey(MyUser,blank=True,null=True,on_delete=models.SET_NULL,related_name='userdelete_formats')
    deleteTime = models.DateTimeField(blank=True,null=True)
    createUser = models.ForeignKey(MyUser,blank=True,null=True,on_delete=models.SET_NULL,related_name='usercreate_formats')
    createTime = models.DateTimeField(auto_now_add=True)
    lastModifyUser = models.ForeignKey(MyUser, blank=True, null=True, on_delete=models.SET_NULL,related_name='usermodify_formats')
    lastModifyTime = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = 'projectFormat'

class finance(models.Model):
    id = models.AutoField(primary_key=True)
    proj = models.ForeignKey(project, blank=True, null=True, related_name='proj_finances',related_query_name='finance')
    revenue = models.IntegerField(blank=True,null=True,)
    netIncome = models.IntegerField(blank=True,null=True,)
    revenue_USD = models.IntegerField(blank=True,null=True,)
    netIncome_USD = models.IntegerField(blank=True,null=True,)
    EBITDA = models.IntegerField(blank=True,null=True,)
    grossProfit = models.IntegerField(blank=True,null=True,)
    totalAsset = models.IntegerField(blank=True,null=True,)
    stockholdersEquity = models.IntegerField(blank=True,null=True,)
    operationalCashFlow = models.IntegerField(blank=True,null=True,)
    grossMerchandiseValue = models.IntegerField(blank=True,null=True,)
    fYear = models.SmallIntegerField(blank=True,null=True,)
    isDeleted = models.BooleanField(blank=True, default=False)
    deleteUser = models.ForeignKey(MyUser, blank=True, null=True, on_delete=models.SET_NULL, related_name='userdelete_finances')
    deleteTime = models.DateTimeField(blank=True, null=True)
    createUser = models.ForeignKey(MyUser, blank=True, null=True, on_delete=models.SET_NULL,related_name='usercreate_finances')
    createTime = models.DateTimeField(auto_now_add=True)
    lastModifyUser = models.ForeignKey(MyUser, blank=True, null=True, on_delete=models.SET_NULL,related_name='usermodify_finances')
    lastModifyTime = models.DateTimeField(auto_now=True)
    def __str__(self):
        if self.proj:
            return self.proj.titleC
        return self.id.__str__()
    class Meta:
        db_table = 'projectFinance'

class projectTags(models.Model):
    proj = models.ForeignKey(project,)
    tag = models.ForeignKey(Tag,related_name='project_tags')
    isdeleted = models.BooleanField(blank=True, default=False)
    deletedUser = models.ForeignKey(MyUser, blank=True, null=True, related_name='userdelete_projtags')
    deletedtime = models.DateTimeField(blank=True, null=True)
    createdtime = models.DateTimeField(auto_created=True)
    createuser = models.ForeignKey(MyUser, blank=True, null=True, related_name='usercreate_projtag',on_delete=models.SET_NULL)

    class Meta:
        db_table = "project_tags"

class projectIndustries(models.Model):
    proj = models.ForeignKey(project, )
    industry = models.ForeignKey(Industry,related_name='project_industries')
    isdeleted = models.BooleanField(blank=True, default=False)
    deletedUser = models.ForeignKey(MyUser, blank=True, null=True, related_name='userdelete_projtags')
    deletedtime = models.DateTimeField(blank=True, null=True)
    createdtime = models.DateTimeField(auto_created=True)
    createuser = models.ForeignKey(MyUser, blank=True, null=True, related_name='usercreate_projtag',on_delete=models.SET_NULL)

    class Meta:
        db_table = "project_industries"

class projectTransactionType(models.Model):
    proj = models.ForeignKey(project, )
    transactionType = models.ForeignKey(Industry, related_name='project_TransactionTypes')
    isdeleted = models.BooleanField(blank=True, default=False)
    deletedUser = models.ForeignKey(MyUser, blank=True, null=True, related_name='userdelete_projtags')
    deletedtime = models.DateTimeField(blank=True, null=True)
    createdtime = models.DateTimeField(auto_created=True)
    createuser = models.ForeignKey(MyUser, blank=True, null=True, related_name='usercreate_projtag',
                                   on_delete=models.SET_NULL)

    class Meta:
        db_table = "project_TransactionType"









#收藏只能 新增/删除/查看/  ，不能修改
class favorite(models.Model):
    proj = models.ForeignKey(project)
    user = models.ForeignKey(MyUser)
    favoritetype = models.ForeignKey(FavoriteType,verbose_name='收藏类型')
    def __str__(self):
        return self.favoritetype.__str__() + self.proj.title + self.user.name
    #单指 新增 操作  ，修改会出问题的
    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        obj = favorite.objects.filter(proj=self.proj,user=self.user,favoritetype=self.favoritetype)
        if obj:
            raise ValueError('已经存在一条相同的记录了')
        else:
            super(favorite, self).save()

    class Meta:
        ordering = ('proj',)
        db_table = 'project_favorite'
