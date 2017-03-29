#coding=utf-8
from __future__ import unicode_literals

import sys
from django.db import models

# Create your models here.
reload(sys)
sys.setdefaultencoding('utf-8')


class AuditStatus(models.Model):
    id = models.AutoField(primary_key=True)
    nameC = models.CharField(max_length=16)
    nameE = models.CharField(max_length=128)
    def __str__(self):
        return self.nameC

class ProjectStatus(models.Model):
    id = models.AutoField(primary_key=True)
    nameC = models.CharField(max_length=16)
    nameE = models.CharField(max_length=128)

    def __str__(self):
        return self.nameC

class OrgType(models.Model):
    id = models.AutoField(primary_key=True)
    nameC = models.CharField(max_length=16)
    nameE = models.CharField(max_length=128)

    def __str__(self):
        return self.nameC

class FavoriteType(models.Model):
    id = models.AutoField(primary_key=True)
    nameC = models.CharField(max_length=16)
    nameE = models.CharField(max_length=128)

    def __str__(self):
        return self.nameC


class MessageType(models.Model):
    id = models.AutoField(primary_key=True)
    nameC = models.CharField(max_length=16)
    nameE = models.CharField(max_length=128)

    def __str__(self):
        return self.nameC

class ClientType(models.Model):
    id = models.AutoField(primary_key=True)
    nameC = models.CharField(max_length=16)
    nameE = models.CharField(max_length=128)

    def __str__(self):
        return self.nameC

class TitleType(models.Model):
    id = models.AutoField(primary_key=True)
    nameC = models.CharField(max_length=16)
    nameE = models.CharField(max_length=128)
    def __str__(self):
        return self.nameC


class Continent(models.Model):
    id = models.AutoField(primary_key=True)
    continentC = models.CharField(max_length=16)
    continentE = models.CharField(max_length=32)
    def __str__(self):
        return self.continentC

class Country(models.Model):
    id = models.AutoField(primary_key=True)
    continent = models.ForeignKey(Continent,related_name='countries',related_query_name='continent')
    countryC = models.CharField(max_length=16)
    countryE = models.CharField(max_length=32)
    areaCode = models.CharField(max_length=8)
    def __str__(self):
        return self.countryC

class CurrencyType(models.Model):
    id = models.AutoField(primary_key=True)
    currencyC = models.CharField(max_length=16)
    currencyE = models.CharField(max_length=8)
    def __str__(self):
        return self.currencyC


class Industry(models.Model):
    id = models.AutoField(primary_key=True)
    Pindustry = models.SmallIntegerField()
    industryC = models.CharField(max_length=16)
    industryE = models.CharField(max_length=32)
    bucket = models.CharField(max_length=8)
    key = models.CharField(max_length=64)
    def __str__(self):
        return self.countryC


class Tag(models.Model):
    id = models.AutoField(primary_key=True)
    nameC = models.CharField(max_length=16)
    nameE = models.CharField(max_length=16)
    hotpoint = models.SmallIntegerField(blank=True,default=0)
    def __str__(self):
        return self.nameC


class OrgArea(models.Model):
    id = models.AutoField(primary_key=True)
    nameC = models.CharField(max_length=16)
    def __str__(self):
        return self.nameC


class School(models.Model):
    id = models.AutoField(primary_key=True)
    nameC = models.TextField(blank=True,default='无')
    nameE = models.TextField(blank=True,default='none')
    def __str__(self):
        return self.nameC


class Profession(models.Model):
    id = models.AutoField(primary_key=True)
    nameC = models.TextField(blank=True,default='无')
    nameE = models.TextField(blank=True,default='none')
    def __str__(self):
        return self.nameC

class TransactionPhases(models.Model):
    id = models.AutoField(primary_key=True)
    nameC = models.CharField(max_length=16)
    nameE = models.CharField(max_length=32)
    def __str__(self):
        return self.nameC

class TransactionType(models.Model):
    id = models.AutoField(primary_key=True)
    nameC = models.CharField(max_length=16)
    nameE = models.CharField(max_length=32)
    def __str__(self):
        return self.nameC