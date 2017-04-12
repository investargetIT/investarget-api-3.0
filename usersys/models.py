#coding=utf-8
from __future__ import unicode_literals

import binascii
import os

import datetime
import random
from time import timezone

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.db.models import Q
from guardian.shortcuts import remove_perm, assign_perm

from sourcetype.models import AuditStatus, ClientType, TitleType,School,Specialty,Tag


class MyUserBackend(ModelBackend):
    def authenticate(self, mobile=None, pwd=None, email=None):
        try:
            if mobile:
                user = MyUser.objects.get(mobile=mobile,is_deleted=False)
            else:
                user = MyUser.objects.get(email=email,is_deleted=False)
        except MyUser.DoesNotExist:
            pass
        else:
            if user.check_password(pwd):
                return user
        return None

    def get_user(self, user_id):
        try:
            return MyUser.objects.get(pk=user_id)
        except MyUser.DoesNotExist:
            return None

class MyUserManager(BaseUserManager):
    def create_user(self,email,mobile=None,password=None,**extra_fields):
        if not email:
            raise ValueError('Users must have an email address')

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
    usercode = models.CharField(max_length=128,blank=True, unique=True)
    photoBucket = models.CharField(max_length=32,blank=True,null=True)
    photoKey = models.CharField(max_length=64,blank=True,null=True)
    cardBucket = models.CharField(max_length=32,blank=True,null=True)
    cardKey = models.CharField(max_length=64,blank=True,null=True)
    wechat = models.CharField(max_length=64,blank=True,null=True)
    userstatu = models.ForeignKey(AuditStatus,help_text='作者',blank=True,null=True)
    org = models.ForeignKey('org.organization',help_text='所属机构',blank=True,null=True,related_name='org_users',on_delete=models.SET_NULL)
    name = models.CharField(help_text='姓名',max_length=128,db_index=True,blank=True,null=True)
    nameE = models.CharField(help_text='name',max_length=128,db_index=True,blank=True,null=True)
    mobileAreaCode = models.CharField(max_length=3,blank=True,null=True,default='86')
    mobile = models.CharField(help_text='手机',max_length=32,db_index=True,blank=True,null=True)
    company = models.CharField(max_length=64,blank=True,null=True)
    description = models.TextField(help_text='简介',blank=True,default='description')
    tags = models.ManyToManyField(Tag, through='userTags', through_fields=('user', 'tag'), blank=True)
    email = models.EmailField(help_text='邮箱', max_length=48,db_index=True,blank=True,null=True)
    title = models.ForeignKey(TitleType,blank=True,null=True,related_name='title_users',related_query_name='user_title',on_delete=models.SET_NULL)
    gender = models.BooleanField(blank=True,default=0,help_text=('0=男，1=女'))
    remark = models.TextField(help_text='简介',blank=True,null=True)
    school = models.ForeignKey(School,help_text='院校',blank=True,null=True,related_name='school_users',on_delete=models.SET_NULL)
    specialty = models.ForeignKey(Specialty,help_text='专业',blank=True,null=True,related_name='profession_users',on_delete=models.SET_NULL)
    registersource = models.SmallIntegerField(help_text='注册来源',choices=((1,'pc'),(2,'ios'),(3,'android'),(4,'mobileweb')),default=1)
    lastmodifytime = models.DateTimeField(auto_now=True)
    lastmodifyuser = models.ForeignKey('self',help_text='修改者',blank=True,null=True,related_name='usermodify_users',related_query_name='user_modifyuser',on_delete=models.SET_NULL)
    is_staff = models.BooleanField(help_text='登录admin', default=False, blank=True,)
    is_active = models.BooleanField(help_text='是否活跃', default=True, blank=True,)
    is_deleted = models.BooleanField(blank=True,help_text='是否已被删除', default=False)
    deleteduser = models.ForeignKey('self',help_text='删除者',blank=True,null=True,related_name='userdelete_users',related_query_name='user_deleteduser',on_delete=models.SET_NULL)
    deletedtime = models.DateTimeField(blank=True,null=True)
    createdtime = models.DateTimeField(auto_now_add=True,blank=True)
    createuser = models.ForeignKey('self',help_text='创建者',blank=True,null=True,related_name='usercreate_users',related_query_name='user_createuser',on_delete=models.SET_NULL)

    USERNAME_FIELD = 'usercode'
    REQUIRED_FIELDS = ['email']


    objects = MyUserManager()  # 在这里关联自定义的UserManager
    def get_full_name(self):
        return self.name
    def get_short_name(self):
        return self.name
    def __unicode__(self):
        return self.name
    class Meta:
        db_table = "user"
        permissions = (
            ('as_investoruser', u'投资人'),
            ('as_traderuser', u'交易师'),
            ('as_supporteruser', u'项目方'),
            ('as_adminuser', u'普通管理员'),
            ('trader_adduser', u'交易师新增'),
            ('admin_adduser',u'管理员新增'),
            ('trader_changeuser', u'交易师编辑'),
            ('admin_changeuser',u'管理员编辑')
        )
    def save(self, *args, **kwargs):
        if not self.usercode:
            self.usercode = str(datetime.datetime.now())
        try:
            if not self.email and not self.mobile:
                raise ValueError('mobile ，email都为空')
            if self.pk:
                MyUser.objects.exclude(pk=self.pk).get(Q(is_deleted=False),Q(mobile=self.mobile) | Q(email=self.email))
            else:
                MyUser.objects.get(Q(is_deleted=False),Q(mobile=self.mobile) | Q(email=self.email))
        except MyUser.DoesNotExist:
            pass
        else:
            raise ValueError('mobile或email已存在')
        super(MyUser,self).save(*args,**kwargs)

class userTags(models.Model):
    user = models.ForeignKey(MyUser,null=True,blank=True,on_delete=models.SET_NULL)
    tag = models.ForeignKey(Tag, related_name='user_tags',null=True, blank=True,on_delete=models.SET_NULL)
    isdeleted = models.BooleanField(blank=True,default=False)
    deleteduser = models.ForeignKey(MyUser,blank=True, null=True,related_name='userdelete_tags',on_delete=models.SET_NULL)
    deletedtime = models.DateTimeField(blank=True, null=True)
    createdtime = models.DateTimeField(auto_created=True)
    createuser = models.ForeignKey(MyUser,blank=True, null=True,related_name='usercreate_usertags',on_delete=models.SET_NULL)
    class Meta:
        db_table = "user_tags"



class MyToken(models.Model):
    key = models.CharField('Key', max_length=48, primary_key=True)
    user = models.ForeignKey(MyUser, related_name='user_token',on_delete=models.CASCADE, verbose_name=("MyUser"))
    created = models.DateTimeField(("Created"), auto_now_add=True)
    clienttype = models.ForeignKey(ClientType)
    is_deleted = models.BooleanField(verbose_name='是否已被删除',blank=True,default=False)
    class Meta:
        db_table = 'user_token'
    def timeout(self):
        return datetime.timedelta(hours=24 * 1) - (datetime.datetime.utcnow() - self.created.replace(tzinfo=None))

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(MyToken, self).save(*args, **kwargs)

    def generate_key(self):
        return binascii.hexlify(os.urandom(24)).decode()

    def __str__(self):
        return self.key

class UserRelation(models.Model):
    investoruser = models.ForeignKey(MyUser,related_name='investor_relations',help_text=('作为投资人'))
    traderuser = models.ForeignKey(MyUser,related_name='trader_relations',help_text=('作为交易师'))
    relationtype = models.BooleanField(help_text=('强关系True，弱关系False'),default=False)
    score = models.SmallIntegerField(help_text=('交易师评分'), default=0, blank=True)
    is_deleted = models.BooleanField(blank=True, default=False)
    deleteduser = models.ForeignKey(MyUser, blank=True, null=True, related_name='userdelete_relations')
    deletedtime = models.DateTimeField(blank=True, null=True)
    createdtime = models.DateTimeField(auto_now_add=True)
    createuser = models.ForeignKey(MyUser, blank=True, null=True, related_name='usercreate_relations',
                                   on_delete=models.SET_NULL)
    lastmodifytime = models.DateTimeField(blank=True, null=True)
    lastmodifyuser = models.ForeignKey(MyUser, blank=True, null=True, related_name='usermodify_relations', )
    def save(self, *args, **kwargs):
        if self.pk:
            userrelation = UserRelation.objects.exclude(pk=self.pk).filter(Q(is_deleted=False), Q(investoruser=self.investoruser))
        else:
            userrelation = UserRelation.objects.filter(Q(is_deleted=False), Q(investoruser=self.investoruser))
        if userrelation.exists():
            if userrelation.filter(traderuser_id=self.traderuser_id).exists():
                raise ValueError('2.已经存在一条这两名用户的记录了')
            elif userrelation.filter(relationtype=True).exists() and self.relationtype:
                raise ValueError('3.强关系只能有一个,如有必要，先删除，在添加')
        else:
            self.relationtype = True
        if self.investoruser.id == self.traderuser.id:
            raise ValueError('1.投资人和交易师不能是同一个人')
        elif not self.traderuser.has_perm('as_traderuser'):
            raise ValueError('4.没有交易师权限关系')
        elif not self.investoruser.has_perm('as_investoruser'):
            raise ValueError('5.没有投资人权限')
        else:
            if self.pk:
                if self.is_deleted:
                    remove_perm('MyUserSys.trader_change',self.traderuser,self.investoruser)
                    remove_perm('MyUserSys.change_userrelation', self.traderuser, self)
                    remove_perm('MyUserSys.delete_userrelation', self.traderuser, self)
                else:
                    oldrela = UserRelation.objects.get(pk=self.pk)
                    remove_perm('MyUserSys.trader_change',oldrela.traderuser,oldrela.investoruser)
                    remove_perm('MyUserSys.change_userrelation', oldrela.traderuser, self)
                    remove_perm('MyUserSys.delete_userrelation', oldrela.traderuser, self)
                    assign_perm('MyUserSys.trader_change',self.traderuser,self.investoruser)
                    assign_perm('MyUserSys.change_userrelation', self.traderuser, self)
                    assign_perm('MyUserSys.delete_userrelation', self.traderuser, self)
            else:
                assign_perm('MyUserSys.trader_change', self.traderuser, self.investoruser)
                assign_perm('MyUserSys.change_userrelation', self.traderuser, self)
                assign_perm('MyUserSys.delete_userrelation', self.traderuser, self)
            super(UserRelation, self).save(*args, **kwargs)
    class Meta:
        db_table = "user_relation"
        permissions =  (
            ('admin_adduserrelation', u'管理员建立用户联系'),
            ('admin_changeuserrelation', u'管理员修改用户联系'),
            ('admin_deleteuserrelation', u'管理员删除用户联系'),
        )


class MobileAuthCode(models.Model):
    mobile = models.CharField(help_text='手机号',max_length=32)
    token = models.CharField(help_text='验证码token',max_length=32)
    code = models.CharField(help_text='验证码',max_length=32)
    createTime = models.DateTimeField(auto_now_add=True)
    def isexpired(self):
        return timezone.now() - self.created >= 600
    def __str__(self):
        return self.code
    class Meta:
        db_table = "mobileAuthCode"
    def save(self, *args, **kwargs):
        if not self.token:
            self.token = binascii.hexlify(os.urandom(16)).decode()
        return super(MobileAuthCode, self).save(*args, **kwargs)
    def getRandomCode(self):
        code_list = [0,1,2,3,4,5,6,7,8,9]
        myslice = random.sample(code_list, 6)
        self.code = ''.join(myslice)