#coding=utf-8
from __future__ import unicode_literals

import sys
from django.db import models

# Create your models here.
reload(sys)
sys.setdefaultencoding('utf-8')


class auditStatus(models.Model):
    id = models.AutoField(primary_key=True)
    nameC = models.CharField(max_length=16)
    nameE = models.CharField(max_length=128)
    def __str__(self):
        return self.nameC

class projectStatus(models.Model):
    id = models.AutoField(primary_key=True)
    nameC = models.CharField(max_length=16)
    nameE = models.CharField(max_length=128)

    def __str__(self):
        return self.nameC

class orgType(models.Model):
    id = models.AutoField(primary_key=True)
    nameC = models.CharField(max_length=16)
    nameE = models.CharField(max_length=128)

    def __str__(self):
        return self.nameC

class favoriteType(models.Model):
    id = models.AutoField(primary_key=True)
    nameC = models.CharField(max_length=16)
    nameE = models.CharField(max_length=128)

    def __str__(self):
        return self.nameC


class messageType(models.Model):
    id = models.AutoField(primary_key=True)
    nameC = models.CharField(max_length=16)
    nameE = models.CharField(max_length=128)

    def __str__(self):
        return self.nameC

class clientType(models.Model):
    id = models.AutoField(primary_key=True)
    nameC = models.CharField(max_length=16)
    nameE = models.CharField(max_length=128)

    def __str__(self):
        return self.nameC

class titleType(models.Model):
    id = models.AutoField(primary_key=True)
    nameC = models.CharField(max_length=16)
    nameE = models.CharField(max_length=128)
    def __str__(self):
        return self.nameC


class continent(models.Model):
    id = models.AutoField(primary_key=True)
    continentC = models.CharField(max_length=16)
    continentE = models.CharField(max_length=32)
    def __str__(self):
        return self.continentC

class country(models.Model):
    id = models.AutoField(primary_key=True)
    continent = models.ForeignKey(continent,related_name='countries',related_query_name='continent')
    countryC = models.CharField(max_length=16)
    countryE = models.CharField(max_length=32)
    areaCode = models.CharField(max_length=8)
    def __str__(self):
        return self.countryC

class currencyType(models.Model):
    id = models.AutoField(primary_key=True)
    currencyC = models.CharField(max_length=16)
    currencyE = models.CharField(max_length=8)
    def __str__(self):
        return self.currencyC


class industry(models.Model):
    id = models.AutoField(primary_key=True)
    Pindustry = models.SmallIntegerField()
    industryC = models.CharField(max_length=16)
    industryE = models.CharField(max_length=32)
    bucket = models.CharField(max_length=8)
    key = models.CharField(max_length=64)
    def __str__(self):
        return self.countryC


class tag(models.Model):
    id = models.AutoField(primary_key=True)
    nameC = models.CharField(max_length=16)
    nameE = models.CharField(max_length=16)
    hotpoint = models.SmallIntegerField(blank=True,default=0)
    def __str__(self):
        return self.nameC


class orgArea(models.Model):
    id = models.AutoField(primary_key=True)
    nameC = models.CharField(max_length=16)
    def __str__(self):
        return self.nameC


class school(models.Model):
    id = models.AutoField(primary_key=True)
    nameC = models.TextField(blank=True,default='无')
    nameE = models.TextField(blank=True,default='none')
    def __str__(self):
        return self.nameC


class profession(models.Model):
    id = models.AutoField(primary_key=True)
    nameC = models.TextField(blank=True,default='无')
    nameE = models.TextField(blank=True,default='none')
    def __str__(self):
        return self.nameC

class transactionPhases(models.Model):
    id = models.AutoField(primary_key=True)
    nameC = models.CharField(max_length=16)
    nameE = models.CharField(max_length=32)
    def __str__(self):
        return self.nameC

class transactionType(models.Model):
    id = models.AutoField(primary_key=True)
    nameC = models.CharField(max_length=16)
    nameE = models.CharField(max_length=32)
    def __str__(self):
        return self.nameC