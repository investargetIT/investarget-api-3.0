#coding=utf-8
from __future__ import unicode_literals

import binascii
import os

import datetime
from time import timezone

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from org.models import organization
from types.models import auditStatus, clientType, titleType,school,profession,tag


class MyUserBackend(ModelBackend):
    def authenticate(self, mobile=None, pwd=None, email=None):

        try:
            if mobile:
                user = MyUser.objects.get(mobile=mobile)
            else:
                user = MyUser.objects.get(email=email)
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
            is_staff=False,
            is_active=True,
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
    photoBucket = models.CharField(max_length=32,blank=True,null=True)
    photoKey = models.CharField(max_length=64,blank=True,null=True)
    cardBucket = models.CharField(max_length=32,blank=True,null=True)
    cardKey = models.CharField(max_length=64,blank=True,null=True)
    wechat = models.CharField(max_length=64,blank=True,null=True)
    userstatu = models.ForeignKey(auditStatus,verbose_name='作者',blank=True,default=1)
    org = models.ForeignKey(organization,verbose_name='所属机构',blank=True,null=True,related_name='org_users',on_delete=models.SET_NULL)
    name = models.CharField(verbose_name='姓名',max_length=128,db_index=True)
    nameE = models.CharField(verbose_name='name',max_length=128,db_index=True,blank=True,null=True)
    mobileAreaCode = models.CharField(max_length=3,blank=True,null=True,default='86')
    mobile = models.CharField(verbose_name='手机',max_length=32,unique=True,db_index=True)
    company = models.CharField(max_length=64,blank=True,null=True)
    description = models.TextField(verbose_name='简介',blank=True,default='description')
    email = models.EmailField(verbose_name='邮箱', max_length=48,db_index=True)
    tag = models.ManyToManyField(tag,through='userTags',through_fields=('user','tag'))
    title = models.ForeignKey(titleType,blank=True,null=True,related_name='title_users',related_query_name='user_title',on_delete=models.SET_NULL)
    gender = models.BooleanField(blank=True,default=0,help_text=('0=男，1=女'))
    remark = models.TextField(verbose_name='简介',blank=True,null=True)
    school = models.ForeignKey(school,verbose_name='院校',blank=True,null=True,related_name='school_users',on_delete=models.SET_NULL)
    profes = models.ForeignKey(profession,verbose_name='专业',blank=True,null=True,related_name='profession_users',on_delete=models.SET_NULL)
    trader = models.ForeignKey('self',verbose_name='交易师',blank=True,null=True,related_name='trader_users',on_delete=models.SET_NULL)
    registersource = models.SmallIntegerField(verbose_name='注册来源',choices=((1,'pc'),(2,'ios'),(3,'android'),(4,'mobileweb')),default=1)
    lastmodifytime = models.DateTimeField(auto_now=True)
    lastmodifyuser = models.ForeignKey('self',verbose_name='修改者',blank=True,null=True,related_name='usermodify_users',related_query_name='user_modifyuser',on_delete=models.SET_NULL)
    is_staff = models.BooleanField(verbose_name='登录admin', default=False)
    is_active = models.BooleanField(verbose_name='是否活跃', default=True)
    is_deleted = models.BooleanField(verbose_name='是否已被删除', default=False)
    deleteduser = models.ForeignKey('self',verbose_name='删除者',blank=True,null=True,related_name='userdelete_users',related_query_name='user_deleteduser',on_delete=models.SET_NULL)
    deletedtime = models.DateTimeField(blank=True,null=True)
    createdtime = models.DateTimeField(auto_now_add=True)
    createuser = models.ForeignKey('self',verbose_name='创建者',blank=True,null=True,related_name='usercreate_users',related_query_name='user_createuser',on_delete=models.SET_NULL)

    USERNAME_FIELD = 'mobile'
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

class userTags(models.Model):
    user = models.ForeignKey(MyUser,related_name='user_tags')
    tag = models.ForeignKey(tag)
    isdeleted = models.BooleanField(blank=True,default=False)
    deletedUser = models.ForeignKey(MyUser,blank=True, null=True,related_name='userdelete_tags')
    deletedtime = models.DateTimeField(blank=True, null=True)
    createdtime = models.DateTimeField(auto_created=True)
    createuser = models.ForeignKey(MyUser,blank=True, null=True,related_name='usercreate_usertags',on_delete=models.SET_NULL)
    class Meta:
        db_table = "user_tags"



class MyToken(models.Model):
    key = models.CharField('Key', max_length=48, primary_key=True)
    user = models.ForeignKey(
        MyUser, related_name='user_token',
        on_delete=models.CASCADE, verbose_name=("MyUser")
    )
    created = models.DateTimeField(("Created"), auto_now_add=True)
    clienttype = models.ForeignKey(clientType)
    isdeleted = models.BooleanField(verbose_name='是否已被删除',blank=True,default=False)
    class Meta:
        db_table = 'Token'
        verbose_name = ("MyToken")
        verbose_name_plural = ("MyTokens")
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
    investoruser = models.ForeignKey(MyUser,related_name='investorRelation',related_query_name='investor_set',help_text=(
            '作为投资人'
        ),)
    traderuser = models.ForeignKey(MyUser,related_name='traderRelation',related_query_name='trader_set',help_text=(
            '作为交易师'
        ),)
    relationtype = models.BooleanField('强弱关系',help_text=('强关系True，弱关系False'),default=False)
    score = models.SmallIntegerField('交易师评分',default=0,blank=True)
    def save(self, *args, **kwargs):
        try:
            strong = UserRelation.objects.get(investoruser=self.investoruser, relationtype=True)
        except UserRelation.DoesNotExist:
            strongrelate = None
        else:
            strongrelate = strong
        if self.investoruser.id == self.traderuser.id:
            raise ValueError('1投资人和交易师不能是同一个人')
        elif UserRelation.objects.get(investoruser=self.investoruser,traderuser=self.traderuser):
            raise ValueError('2已经存在一条这两名用户的记录了')
        # elif strongrelate and kwargs.get('add') and self.relationtype == True:
        #     raise ValueError('3强关系只能有一个')
        elif strongrelate and self.id != strongrelate.id and self.relationtype == True:
            raise ValueError('6强关系只能有一个')
        elif self.traderuser.usertype_id == 1:
            raise ValueError('4投资人不能作为交易师与其他用户建立关系')
        elif self.investoruser.usertype_id == 2:
            raise ValueError('5交易师不能作为投资人与其他用户建立关系')
        else:
            super(UserRelation, self).save(*args, **kwargs)
    class Meta:
        db_table = "UserRelation"

class MobileAuthCode(models.Model):
    mobile = models.CharField(verbose_name='手机号',unique=True,max_length=32)
    token = models.CharField(verbose_name='验证码token',max_length=128)
    code = models.CharField(verbose_name='验证码',max_length=32)
    created = models.DateTimeField(auto_now_add=True)
    def isexpired(self):
        return timezone.now() - self.created >= 600
    def __str__(self):
        return self.code + self.mobile
    class Meta:
        db_table = "MobileAuthCode"