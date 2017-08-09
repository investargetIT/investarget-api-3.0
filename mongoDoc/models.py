#coding:utf-8
from __future__ import unicode_literals

import datetime
from mongoengine import *
from invest.settings import MongoTableName


# class WXContentData(Document):
#     name = StringField()
#     content = StringField()
#     group_name = StringField()
#     createtime = DateTimeField()
#     meta = {"collection": "aaa"}



class GroupEmailData(Document):
    users = ListField(DictField())
    projtitle = StringField()
    proj = DictField()
    savetime = DateTimeField(default=datetime.datetime.now())
    datasource = IntField()
    meta = {"collection": MongoTableName}