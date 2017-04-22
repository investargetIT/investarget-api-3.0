#coding=utf8
from __future__ import unicode_literals

from django.db import models

# Create your models here.
from sourcetype.models import FavoriteType, ProjectStatus,CurrencyType,Tag,Country,TransactionType,Industry, DataSource
from usersys.models import MyUser
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


class project(models.Model):
    id = models.AutoField(primary_key=True)
    titleC = models.CharField(max_length=128,db_index=True,default='标题')
    titleE = models.CharField(max_length=256,blank=True,null=True,db_index=True)
    statu = models.ForeignKey(ProjectStatus,help_text='项目状态',default=1)
    c_descriptionC = models.TextField(blank=True, default='公司介绍')
    c_descriptionE = models.TextField(blank=True, default='company description')
    p_introducteC = models.TextField(blank=True, default='项目介绍')
    p_introducteE = models.TextField(blank=True, default='project introduction')
    isoverseasproject = models.BooleanField(blank=True,default=True,help_text='是否是海外项目')
    supportUser = models.ForeignKey(MyUser,blank=True,null=True,related_name='usersupport_projs',on_delete=models.SET_NULL)
    isHidden = models.BooleanField(blank=True,default=False)
    financeAmount = models.BigIntegerField(blank=True,null=True)
    financeAmount_USD = models.BigIntegerField(blank=True,null=True)
    companyValuation = models.BigIntegerField(help_text='公司估值', blank=True, null=True)
    companyValuation_USD = models.BigIntegerField(help_text='公司估值', blank=True, null=True)
    companyYear = models.SmallIntegerField(help_text='公司年限', blank=True, null=True)
    financeIsPublic = models.BooleanField(blank=True, default=True)
    code = models.CharField(max_length=128, blank=True, null=True)
    currency = models.ForeignKey(CurrencyType,default=1,on_delete=models.SET_NULL,null=True)
    tags = models.ManyToManyField(Tag, through='projectTags', through_fields=('proj', 'tag'),blank=True)
    industries = models.ManyToManyField(Industry, through='projectIndustries', through_fields=('proj', 'industry'),blank=True)
    transactionType = models.ManyToManyField(TransactionType, through='projectTransactionType',through_fields=('proj', 'transactionType'),blank=True)
    contactPerson = models.CharField(help_text='联系人',max_length=64,blank=True,null=True)
    phoneNumber = models.CharField(max_length=32,blank=True,null=True)
    email = models.EmailField(help_text='联系人邮箱', max_length=48, db_index=True,blank=True,null=True)
    country = models.ForeignKey(Country,blank=True,null=True,db_index=True)
    targetMarketC = models.TextField(help_text='目标市场', blank=True, null=True)
    targetMarketE = models.TextField(blank=True, null=True)
    productTechnologyC = models.TextField(help_text='核心技术', blank=True, null=True)
    productTechnologyE = models.TextField(blank=True, null=True)
    businessModelC = models.TextField(help_text='商业模式', blank=True, null=True)
    businessModelE = models.TextField(blank=True, null=True)
    brandChannelC = models.TextField(help_text='品牌渠道', blank=True, null=True)
    brandChannelE = models.TextField(null=True, blank=True)
    managementTeamC = models.TextField(help_text='管理团队', blank=True, null=True)
    managementTeamE = models.TextField(blank=True, null=True)
    BusinesspartnersC = models.TextField(help_text='商业伙伴', null=True, blank=True)
    BusinesspartnersE = models.TextField(null=True, blank=True)
    useOfProceedC = models.TextField(help_text='资金用途', blank=True, null=True)
    useOfProceedE = models.TextField(blank=True, null=True)
    financingHistoryC = models.TextField(help_text='融资历史', blank=True, null=True)
    financingHistoryE = models.TextField(blank=True, null=True)
    operationalDataC = models.TextField(help_text='经营数据', blank=True, null=True)
    operationalDataE = models.TextField(blank=True, null=True)
    is_deleted = models.BooleanField(blank=True, default=False)
    deleteuser = models.ForeignKey(MyUser, blank=True, null=True, on_delete=models.SET_NULL,related_name='userdelete_projects')
    deletetime = models.DateTimeField(blank=True, null=True)
    createuser = models.ForeignKey(MyUser, blank=True, null=True, on_delete=models.SET_NULL,related_name='usercreate_projects')
    createtime = models.DateTimeField(auto_now_add=True)
    lastmodifyuser = models.ForeignKey(MyUser, blank=True, null=True, on_delete=models.SET_NULL,related_name='usermodify_projects')
    lastmodifytime = models.DateTimeField(auto_now=True)
    datasource = models.ForeignKey(DataSource, help_text='数据源')
    def __str__(self):
        return self.titleC
    class Meta:
        db_table = 'project'
        permissions = (
            ('admin_addproj','管理员上传项目'),
            ('admin_changeproj', '管理员修改项目'),
            ('admin_deleteproj', '管理员删除项目'),
            ('admin_getproj', '管理员查看项目'),

            ('user_addproj', '用户上传项目'),
            ('user_changeproj', '用户修改项目(obj级别)'),
            ('user_deleteproj', '用户删除项目(obj级别)'),
            ('user_getproj','用户查看项目(obj/class级别)'),

        )

class finance(models.Model):
    id = models.AutoField(primary_key=True)
    proj = models.ForeignKey(project, blank=True, null=True, related_name='proj_finances', related_query_name='finance')
    revenue = models.BigIntegerField(blank=True, null=True, )
    netIncome = models.BigIntegerField(blank=True, null=True, )
    revenue_USD = models.BigIntegerField(blank=True, null=True, )
    netIncome_USD = models.BigIntegerField(blank=True, null=True, )
    EBITDA = models.BigIntegerField(blank=True, null=True, )
    grossProfit = models.BigIntegerField(blank=True, null=True, )
    totalAsset = models.BigIntegerField(blank=True, null=True, )
    stockholdersEquity = models.BigIntegerField(blank=True, null=True, )
    operationalCashFlow = models.BigIntegerField(blank=True, null=True, )
    grossMerchandiseValue = models.BigIntegerField(blank=True, null=True, )
    fYear = models.SmallIntegerField(blank=True, null=True, )
    is_deleted = models.BooleanField(blank=True, default=False)
    deleteuser = models.ForeignKey(MyUser, blank=True, null=True, on_delete=models.SET_NULL,related_name='userdelete_finances')
    deletetime = models.DateTimeField(blank=True, null=True)
    createuser = models.ForeignKey(MyUser, blank=True, null=True, on_delete=models.SET_NULL, related_name='usercreate_finances')
    createtime = models.DateTimeField(auto_now_add=True)
    lastmodifyuser = models.ForeignKey(MyUser, blank=True, null=True, on_delete=models.SET_NULL,related_name='usermodify_finances')
    lastmodifytime = models.DateTimeField(auto_now=True)
    datasource = models.ForeignKey(DataSource, help_text='数据源')
    def __str__(self):
        if self.proj:
            return self.proj.titleC
        return self.id.__str__()

    class Meta:
        db_table = 'projectFinance'


class projectTags(models.Model):
    proj = models.ForeignKey(project,related_name='project_tags' )
    tag = models.ForeignKey(Tag, related_name='tag_projects')
    is_deleted = models.BooleanField(blank=True, default=False)
    deleteduser = models.ForeignKey(MyUser, blank=True, null=True, related_name='userdelete_projtags')
    deletedtime = models.DateTimeField(blank=True, null=True)
    createdtime = models.DateTimeField(auto_created=True)
    createuser = models.ForeignKey(MyUser, blank=True, null=True, related_name='usercreate_projtag')

    class Meta:
        db_table = "project_tags"


class projectIndustries(models.Model):
    proj = models.ForeignKey(project,related_name='project_industries')
    industry = models.ForeignKey(Industry, related_name='industry_projects')
    is_deleted = models.BooleanField(blank=True, default=False)
    deleteduser = models.ForeignKey(MyUser, blank=True, null=True, related_name='userdelete_projIndustries')
    deletedtime = models.DateTimeField(blank=True, null=True)
    createdtime = models.DateTimeField(auto_created=True)
    createuser = models.ForeignKey(MyUser, blank=True, null=True, related_name='usercreate_projIndustry')

    class Meta:
        db_table = "project_industries"


class projectTransactionType(models.Model):
    proj = models.ForeignKey(project, related_name='project_TransactionTypes')
    transactionType = models.ForeignKey(TransactionType, related_name='transactionType_projects')
    is_deleted = models.BooleanField(blank=True, default=False)
    deleteduser = models.ForeignKey(MyUser, blank=True, null=True, related_name='userdelete_projtransactionTypes')
    deletedtime = models.DateTimeField(blank=True, null=True)
    createdtime = models.DateTimeField(auto_created=True)
    createuser = models.ForeignKey(MyUser, blank=True, null=True, related_name='usercreate_projtransactionType')

    class Meta:
        db_table = "project_TransactionType"



#收藏只能 新增/删除/查看/  ，不能修改
class favoriteProject(models.Model):
    proj = models.ForeignKey(project,related_name='proj_favorite')
    user = models.ForeignKey(MyUser,related_name='user_favorite')
    trader = models.ForeignKey(MyUser,blank=True,null=True,related_name='trader_favorite',help_text='交易师id（用户感兴趣时联系/交易师推荐）')
    favoritetype = models.ForeignKey(FavoriteType,related_name='favoritetype_proj',help_text='收藏类型')
    is_deleted = models.BooleanField(blank=True, default=False)
    deleteduser = models.ForeignKey(MyUser, blank=True, null=True, related_name='userdelete_favoriteproj')
    deletedtime = models.DateTimeField(blank=True, null=True)
    createdtime = models.DateTimeField(auto_created=True)
    createuser = models.ForeignKey(MyUser, blank=True, null=True, related_name='usercreate_favoriteproj')
    datasource = models.ForeignKey(DataSource, help_text='数据源')
    def __str__(self):
        return self.favoritetype.__str__() + self.proj.title + self.user.name
    # #单指 新增 操作  ，修改会出问题的
    # def save(self, force_insert=False, force_update=False, using=None,
    #          update_fields=None):
    #     obj = favorite.objects.filter(proj=self.proj,user=self.user,favoritetype=self.favoritetype)
    #     if obj:
    #         raise ValueError('已经存在一条相同的记录了')
    #     else:
    #         super(favorite, self).save()
    class Meta:
        ordering = ('proj',)
        db_table = 'project_favorite'
        permissions = (
            ('user_addfavorite','用户添加favorite(obj级别——给交易师的)'),
            ('user_getfavorite', '用户查看favorite(obj级别——给交易师的)'),

            ('admin_addfavorite', '管理员添加favorite'),
            ('admin_getfavorite', '管理员查看favorite'),
            ('admin_deletefavorite','管理员删除favorite'),
        )
