#coding=utf-8
from __future__ import unicode_literals

import binascii
import os

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.contrib.auth.models import Group
# Create your models here.
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

from invest import settings
from org.models import organization


class MyUserBackend(ModelBackend):
    def authenticate(self, phone=None, pwd=None):
        try:
            user = MyUser.objects.get(phone=phone)
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
    def create_user(self,email,phone=None,password=None,**extra_fields):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            phone=phone,
            email=MyUserManager.normalize_email(email),
            is_staff=False,
            is_active=True,
            is_superuser=False,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, phone, password):
        user = self.create_user(email,
                                phone,
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
    userstatu = models.IntegerField(verbose_name='作者',choices=((1,'未审核'),(2,'审核通过'),(3,'审核退回')),default=1)
    org = models.ManyToManyField(organization,verbose_name='所属机构',blank=True,null=True,related_name='user_org',related_query_name='org_users')
    name = models.CharField(verbose_name='姓名',max_length=100,db_index=True)
    phone = models.CharField(verbose_name='手机',max_length=20,unique=True,db_index=True)
    say = models.CharField(verbose_name='简介',max_length=255,blank=True,null=True)
    email = models.EmailField(verbose_name='邮箱', max_length=254,db_index=True)
    trader = models.ForeignKey('self',verbose_name='交易师',blank=True,null=True,default=None)
    usertype = models.IntegerField(verbose_name='用户类型',choices=((1,'投资人'),(2,'交易师'),(3,'项目方'),(4,'管理员')))
    is_staff = models.BooleanField(verbose_name='登录admin', default=False)
    is_active = models.BooleanField(verbose_name='是否活跃', default=True)
    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['email']

    objects = MyUserManager()  # 在这里关联自定义的UserManager
    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name

    def __unicode__(self):
        return self.name


class MyToken(models.Model):
    key = models.CharField('Key', max_length=40, primary_key=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, related_name='user_token',
        on_delete=models.CASCADE, verbose_name=("MyUser")
    )

    created = models.DateTimeField(("Created"), auto_now_add=True)
    clienttype = models.IntegerField(choices=((1,'ios'),(2,'android'),(3,'pc'),(4,'mobweb')))
    class Meta:
        verbose_name = ("MyToken")
        verbose_name_plural = ("MyTokens")

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(MyToken, self).save(*args, **kwargs)

    def generate_key(self):
        return binascii.hexlify(os.urandom(20)).decode()

    def __str__(self):
        return self.key

class UserRelation(models.Model):
    investoruser = models.ForeignKey(MyUser,related_name='investoruser',related_query_name='investor_set',help_text=(
            '作为投资人'
        ),)
    traderuser = models.ForeignKey(MyUser,related_name='traderuser',related_query_name='trader_set',help_text=(
            '作为交易师'
        ),)
    relationtype = models.BooleanField('强弱关系',help_text=('强关系True，弱关系False'),)
    def save(self, *args, **kwargs):
        if self.investoruser.id == self.traderuser.id:
            raise ValueError('1投资人和交易师不能是同一个人')
        elif UserRelation.objects.filter(investoruser=self.investoruser,traderuser=self.traderuser):
            raise ValueError('2已经存在一条这两名用户的记录了')
        elif UserRelation.objects.filter(investoruser=self.investoruser,relationtype=True) and kwargs.get('add') and self.relationtype == True:
            raise ValueError('3强关系只能有一个')
        elif self.traderuser.usertype == 1:
            raise ValueError('4投资人不能作为交易师与其他用户建立关系')
        elif self.investoruser.usertype == 2:
            raise ValueError('5交易师不能作为投资人与其他用户建立关系')
        else:
            super(UserRelation, self).save(*args, **kwargs)


