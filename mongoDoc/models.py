#coding:utf-8
from __future__ import unicode_literals

import datetime
from mongoengine import *
from invest.settings import groupemailMongoTableName, chatMessagegMongoTableName


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
    meta = {"collection": groupemailMongoTableName}


class IMChatMessages(Document):
    msg_id = StringField()
    timestamp = StringField()
    direction = StringField()
    to = StringField()
    chatfrom = StringField()
    chat_type = StringField()
    payload = DictField()
    meta = {"collection": chatMessagegMongoTableName}