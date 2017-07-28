#coding=utf-8
from __future__ import unicode_literals
from pypinyin import slug as hanzizhuanpinpin
import binascii
import os

import datetime
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin, Group
from django.db import models
from django.db.models import Q
from guardian.shortcuts import remove_perm, assign_perm
from sourcetype.models import AuditStatus, ClientType, TitleType,School,Specialty,Tag, DataSource, Country
from utils.customClass import InvestError, MyForeignKey
from utils.makeAvatar import makeAvatar

registersourcechoice = (
    (1,'pc'),
    (2,'ios'),
    (3,'android'),
    (4,'mobileweb')
)

class MyUserBackend(ModelBackend):
    def authenticate(self, username=None, password=None, datasource=None):
        try:
            if '@' not in username:
                user = MyUser.objects.get(mobile=username,is_deleted=False,)
            else:
                user = MyUser.objects.get(email=username,is_deleted=False,)
        except MyUser.DoesNotExist:
            raise InvestError(code=2002)
        # datasource = kwargs.pop('datasource',None)
        # if not datasource:
        #     raise InvestError(code=8888, msg='没有datasource')
        # try:
        #     if '@' not in username:
        #         user = MyUser.objects.get(mobile=username, is_deleted=False, datasource=datasource)
        #     else:
        #         user = MyUser.objects.get(email=username, is_deleted=False, datasource=datasource)
        # except MyUser.DoesNotExist:
        #     raise InvestError(code=2002)
        except Exception as err:
            raise InvestError(code=9999,msg='MyUserBackend/authenticate模块验证失败\n,%s'%err)
        else:
            if user.check_password(password):
                return user
        return None

    def get_user(self, user_id):
        try:
            user = MyUser._default_manager.get(pk=user_id)
        except MyUser.DoesNotExist:
            return None
        return user if not user.is_deleted else None

class MyUserManager(BaseUserManager):
    def create_user(self,email,mobile=None,password=None,**extra_fields):
        if not email:
            raise InvestError(code=20071)
        user = self.model(
            mobile=mobile,
            email=MyUserManager.normalize_email(email),
            is_superuser=False,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, mobile, password):
        user = self.create_user(email,
                                mobile,
                                password,
                                )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

# 在settings里面指定这个User类为AUTH_USER_MODEL
class MyUser(AbstractBaseUser, PermissionsMixin):
    """
    groups : 作为权限组
    """
    id = models.AutoField(primary_key=True)
    userlevel = models.PositiveSmallIntegerField(blank=True,default=0,help_text='用户服务级别')
    usercode = models.CharField(max_length=128,blank=True, unique=True)
    photoBucket = models.CharField(max_length=32,blank=True,default='image')
    photoKey = models.CharField(max_length=128,blank=True,null=True)
    cardBucket = models.CharField(max_length=32,blank=True,default='image')
    cardKey = models.CharField(max_length=128,blank=True,null=True)
    wechat = models.CharField(max_length=64,blank=True,null=True)
    country = MyForeignKey(Country,blank=True,null=True)
    userstatus = MyForeignKey(AuditStatus,help_text='审核状态',blank=True,default=1)
    org = MyForeignKey('org.organization',help_text='所属机构',blank=True,null=True,related_name='org_users',on_delete=models.SET_NULL)
    usernameC = models.CharField(help_text='姓名',max_length=128,db_index=True,blank=True,null=True,)
    usernameE = models.CharField(help_text='name',max_length=128,db_index=True,blank=True,null=True)
    mobileAreaCode = models.CharField(max_length=10,blank=True,null=True,default='86')
    mobile = models.CharField(help_text='手机',max_length=32,db_index=True,blank=True,null=True,)
    description = models.TextField(help_text='简介',blank=True,default='description')
    tags = models.ManyToManyField(Tag, through='userTags', through_fields=('user', 'tag'), blank=True,related_name='tag_users')
    email = models.EmailField(help_text='邮箱', max_length=48,db_index=True,blank=True,null=True)
    title = MyForeignKey(TitleType,blank=True,null=True,related_name='title_users',related_query_name='user_title',on_delete=models.SET_NULL)
    gender = models.BooleanField(blank=True,default=0,help_text=('0=男，1=女'))
    remark = models.TextField(help_text='备注',blank=True,null=True)
    school = MyForeignKey(School,help_text='院校',blank=True,null=True,related_name='school_users',on_delete=models.SET_NULL)
    specialty = MyForeignKey(Specialty,help_text='专业',blank=True,null=True,related_name='profession_users',on_delete=models.SET_NULL)
    registersource = models.SmallIntegerField(help_text='注册来源',choices=registersourcechoice,default=1)
    lastmodifytime = models.DateTimeField(blank=True,null=True)
    lastmodifyuser = MyForeignKey('self',help_text='修改者',blank=True,null=True,related_name='usermodify_users',related_query_name='user_modifyuser',on_delete=models.SET_NULL)
    is_staff = models.BooleanField(help_text='登录admin', default=False, blank=True,)
    is_active = models.BooleanField(help_text='是否活跃', default=True, blank=True,)
    is_deleted = models.BooleanField(blank=True,help_text='是否已被删除', default=False)
    deleteduser = MyForeignKey('self',help_text='删除者',blank=True,null=True,related_name='userdelete_users',related_query_name='user_deleteduser',on_delete=models.SET_NULL)
    deletedtime = models.DateTimeField(blank=True,null=True)
    createdtime = models.DateTimeField(auto_now_add=True,blank=True,null=True)
    createuser = MyForeignKey('self',help_text='创建者',blank=True,null=True,related_name='usercreate_users',related_query_name='user_createuser',on_delete=models.SET_NULL)
    datasource = MyForeignKey(DataSource,help_text='数据源',blank=True,null=True)
    USERNAME_FIELD = 'usercode'
    REQUIRED_FIELDS = ['email']


    objects = MyUserManager()  # 在这里关联自定义的UserManager
    def get_full_name(self):
        return self.usernameC
    def get_short_name(self):
        return self.usernameC
    def __str__(self):
        return self.usernameC
    class Meta:
        db_table = "user"
        permissions = (
            ('as_investor', u'投资人身份类型'),
            ('as_trader', u'交易师身份类型'),
            ('as_admin', u'管理员身份类型'),

            ('user_adduser', u'用户新增用户'),
            ('user_deleteuser', u'用户删除用户(obj级别)'),
            ('user_changeuser', u'用户修改用户(obj级别)'),
            ('user_getuser', u'用户查看用户(obj级别)'),

            ('admin_adduser', u'管理员新增用户'),
            ('admin_deleteuser', u'管理员删除'),
            ('admin_changeuser', u'管理员修改用户基本信息'),
            ('admin_getuser', u'管理员查看用户'),
            ('user_addfavorite', '用户添加favorite(obj级别——给交易师的)'),
            ('user_getfavorite', '用户查看favorite(obj级别——给交易师的)'),
        )
    def save(self, *args, **kwargs):
        if not self.usercode:
            self.usercode = str(datetime.datetime.now())
        if not self.datasource:
            raise InvestError(code=8888,msg='datasource有误')
        if self.pk and self.groups.exists() and self.groups.first().datasource != self.datasource:
            raise InvestError(code=8888,msg='group 与 user datasource不同')
        try:
            if not self.email and not self.mobile:
                raise InvestError(code=2007)
            if self.email:
                filters = Q(email=self.email)
                if self.mobile:
                    filters = Q(mobile=self.mobile) | Q(email=self.email)
            else:
                filters = Q(mobile=self.mobile)
            if self.pk:
                MyUser.objects.exclude(pk=self.pk).get(Q(is_deleted=False,datasource=self.datasource),filters)
            else:
                MyUser.objects.get(Q(is_deleted=False,datasource=self.datasource),filters)
        except MyUser.DoesNotExist:
            pass
        else:
            raise InvestError(code=2004)
        if self.pk:
            olduser = MyUser.objects.get(pk=self.pk,datasource=self.datasource)
            if not self.is_deleted:
                if olduser.org and self.org and olduser.org != self.org:
                    remove_perm('org.user_getorg',self,olduser.org)
                    assign_perm('org.user_getorg',self,self.org)
                elif olduser.org and not self.org:
                    remove_perm('org.user_getorg', self, olduser.org)
                elif not olduser.org and self.org:
                    assign_perm('org.user_getorg', self, self.org)
                if not olduser.createuser and self.createuser:
                    assign_perm('usersys.user_deleteuser', self.createuser, self)
            else:
                if olduser.org:
                    remove_perm('org.user_getorg', self, olduser.org)
                if olduser.createuser:
                    remove_perm('usersys.user_getuser', olduser.createuser, self)
                    remove_perm('usersys.user_changeuser', olduser.createuser, self)
                    remove_perm('usersys.user_deleteuser', olduser.createuser, self)
        if not self.usernameC and self.usernameE:
            self.usernameC = self.usernameE
        if not self.usernameE and self.usernameC:
            self.usernameE = hanzizhuanpinpin(self.usernameC,separator='')
        if not self.createdtime:
            self.createdtime = datetime.datetime.now()
        if not self.photoKey:
            if self.usernameC:
                self.photoKey = makeAvatar(self.usernameC[0:1])
        super(MyUser,self).save(*args,**kwargs)

class userTags(models.Model):
    user = MyForeignKey(MyUser,related_name='user_usertags',null=True,blank=True)
    tag = MyForeignKey(Tag, related_name='tag_usertags',null=True, blank=True)
    is_deleted = models.BooleanField(blank=True,default=False)
    deleteduser = MyForeignKey(MyUser,blank=True, null=True,related_name='userdelete_usertags')
    deletedtime = models.DateTimeField(blank=True, null=True)
    createdtime = models.DateTimeField(auto_created=True,blank=True,null=True)
    createuser = MyForeignKey(MyUser,blank=True, null=True,related_name='usercreate_usertags')
    class Meta:
        db_table = "user_tags"



class MyToken(models.Model):
    key = models.CharField('Key', max_length=48, primary_key=True)
    user = MyForeignKey(MyUser, related_name='user_token',verbose_name=("MyUser"))
    created = models.DateTimeField(help_text="CreatedTime", auto_now_add=True,null=True)
    clienttype = MyForeignKey(ClientType,help_text='登录类型')
    is_deleted = models.BooleanField(help_text='是否已被删除',blank=True,default=False)
    class Meta:
        db_table = 'user_token'
    def timeout(self):
        return datetime.timedelta(hours=24 * 1) - (datetime.datetime.now() - self.created)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(MyToken, self).save(*args, **kwargs)
    def generate_key(self):
        return binascii.hexlify(os.urandom(24)).decode()
    def __str__(self):
        return self.key

class UserRelation(models.Model):
    investoruser = MyForeignKey(MyUser,related_name='investor_relations',help_text=('作为投资人'))
    traderuser = MyForeignKey(MyUser,related_name='trader_relations',help_text=('作为交易师'))
    relationtype = models.BooleanField(help_text=('强关系True，弱关系False'),default=False)
    score = models.SmallIntegerField(help_text=('交易师评分'), default=0, blank=True)
    is_deleted = models.BooleanField(blank=True, default=False)
    deleteduser = MyForeignKey(MyUser, blank=True, null=True, related_name='userdelete_relations')
    deletedtime = models.DateTimeField(blank=True, null=True)
    createdtime = models.DateTimeField(auto_now_add=True,null=True)
    createuser = MyForeignKey(MyUser, blank=True, null=True, related_name='usercreate_relations',
                                   on_delete=models.SET_NULL)
    lastmodifytime = models.DateTimeField(blank=True, null=True)
    lastmodifyuser = MyForeignKey(MyUser, blank=True, null=True, related_name='usermodify_relations',)
    datasource = MyForeignKey(DataSource, help_text='数据源')
    def save(self, *args, **kwargs):
        if not self.datasource:
            raise InvestError(code=8888,msg='datasource有误')
        if self.datasource !=self.traderuser.datasource or self.datasource != self.investoruser.datasource:
            raise InvestError(code=8888,msg='requestuser.datasource不匹配')
        if self.pk:
            userrelation = UserRelation.objects.exclude(pk=self.pk).filter(is_deleted=False,datasource=self.datasource,investoruser=self.investoruser)
        else:
            userrelation = UserRelation.objects.filter(is_deleted=False,datasource=self.datasource, investoruser=self.investoruser)
        if userrelation.exists():
            if userrelation.filter(traderuser_id=self.traderuser_id).exists():
                raise InvestError(code=2012,msg='4.关系已存在')
            elif userrelation.filter(relationtype=True).exists() and self.relationtype:
                raise InvestError(code=2013,msg='3.强关系只能有一个,如有必要，先删除，在添加')
        else:
            self.relationtype = True
        if self.investoruser.id == self.traderuser.id:
            raise InvestError(code=2014,msg='1.投资人和交易师不能是同一个人')
        else:
            if self.pk:
                if self.is_deleted:
                    remove_perm('usersys.user_getuser',self.traderuser,self.investoruser)
                    remove_perm('usersys.user_changeuser', self.traderuser, self.investoruser)
                    remove_perm('usersys.user_deleteuser', self.traderuser, self.investoruser)

                    remove_perm('usersys.user_getuserrelation', self.traderuser, self)
                    remove_perm('usersys.user_changeuserrelation', self.traderuser, self)
                    remove_perm('usersys.user_deleteuserrelation', self.traderuser, self)

                    remove_perm('usersys.user_addfavorite', self.traderuser, self.investoruser)
                    remove_perm('usersys.user_getfavorite', self.traderuser, self.investoruser)
                else:
                    oldrela = UserRelation.objects.get(pk=self.pk)
                    remove_perm('usersys.user_getuser', oldrela.traderuser, oldrela.investoruser)
                    remove_perm('usersys.user_changeuser', oldrela.traderuser, oldrela.investoruser)
                    remove_perm('usersys.user_deleteuser', oldrela.traderuser, oldrela.investoruser)

                    remove_perm('usersys.user_getuserrelation', oldrela.traderuser, self)
                    remove_perm('usersys.user_changeuserrelation', oldrela.traderuser, self)
                    remove_perm('usersys.user_deleteuserrelation', oldrela.traderuser, self)

                    assign_perm('usersys.user_getuser',self.traderuser,self.investoruser)
                    assign_perm('usersys.user_changeuser', self.traderuser, self.investoruser)
                    assign_perm('usersys.user_deleteuser', self.traderuser, self.investoruser)

                    assign_perm('usersys.user_getuserrelation', self.traderuser, self)
                    assign_perm('usersys.user_changeuserrelation', self.traderuser, self)
                    assign_perm('usersys.user_deleteuserrelation', self.traderuser, self)

                    assign_perm('usersys.user_addfavorite', self.traderuser, self.investoruser)
                    assign_perm('usersys.user_getfavorite', self.traderuser, self.investoruser)
            else:
                assign_perm('usersys.user_getuser', self.traderuser, self.investoruser)
                assign_perm('usersys.user_changeuser', self.traderuser, self.investoruser)
                assign_perm('usersys.user_deleteuser', self.traderuser, self.investoruser)
                assign_perm('usersys.user_addfavorite', self.traderuser, self.investoruser)
                assign_perm('usersys.user_getfavorite', self.traderuser, self.investoruser)
            super(UserRelation, self).save(*args, **kwargs)
    class Meta:
        db_table = "user_relation"
        permissions =  (
            ('admin_adduserrelation', u'管理员建立用户联系'),
            ('admin_changeuserrelation', u'管理员修改用户联系'),
            ('admin_deleteuserrelation', u'管理员删除用户联系'),
            ('admin_getuserrelation', u'管理员查看用户联系'),

            ('user_adduserrelation', u'用户建立用户联系'),
            ('user_changeuserrelation', u'用户改用户联系（obj级别）'),
            ('user_deleteuserrelation', u'用户删除用户联系（obj级别）'),
            ('user_getuserrelation', u'用户查看用户联系（obj级别）'),
            ('user_getuserrelationlist', u'用户查看用户联系列表'),

        )



class UserFriendship(models.Model):
    id = models.AutoField(primary_key=True)
    user = MyForeignKey(MyUser,related_name='user_friends',help_text='发起人')
    friend = MyForeignKey(MyUser,related_name='friend_users',help_text='接收人')
    isaccept = models.BooleanField(blank=True,default=False)
    accepttime = models.DateTimeField(blank=True,null=True)
    userallowgetfavoriteproj = models.BooleanField(blank=True,default=True,help_text='发起人允许好友查看自己的项目收藏')
    friendallowgetfavoriteproj = models.BooleanField(blank=True, default=True,help_text='接收人允许好友查看自己的项目收藏')
    is_deleted = models.BooleanField(blank=True, default=False)
    deleteduser = MyForeignKey(MyUser, blank=True, null=True, related_name='userdelete_userfriends',)
    deletedtime = models.DateTimeField(blank=True, null=True)
    createdtime = models.DateTimeField(auto_created=True, blank=True,null=True)
    createuser = MyForeignKey(MyUser, blank=True, null=True, related_name='usercreate_userfriends',)
    datasource = MyForeignKey(DataSource, help_text='数据源')
    class Meta:
        db_table = "user_friendship"
        permissions =  (
            ('admin_addfriend', u'管理员建立用户好友关系'),
            ('admin_changefriend', u'管理员修改用户好友关系'),
            ('admin_deletefriend', u'管理员删除用户好友关系'),
            ('admin_getfriend', u'管理员查看用户好友关系'),

            ('user_addfriend', u'用户建立用户好友关系（未审核用户不知道给不给）'),

        )

    def save(self, *args, **kwargs):
        if not self.datasource:
            raise InvestError(code=8888,msg='datasource有误')
        if self.datasource !=self.user.datasource or self.datasource !=self.friend.datasource:
            raise InvestError(code=8888,msg='requestuser.datasource不匹配')
        if self.user == self.friend:
            raise InvestError(2016)
        if not self.accepttime and self.isaccept:
            self.accepttime = datetime.datetime.now()
        if not self.pk:
            if UserFriendship.objects.filter(Q(user=self.user,friend=self.friend,is_deleted=False) | Q(friend=self.user,user=self.friend,is_deleted=False)).exists():
                raise InvestError(2017)
        if not self.createdtime:
            self.createdtime = datetime.datetime.now()
        super(UserFriendship,self).save(*args, **kwargs)

