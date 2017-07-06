#coding:utf-8
from __future__ import unicode_literals

from mongoengine import *



class WXContentData(Document):
    name = StringField()
    content = StringField()
    group_name = StringField()
    createtime = DateTimeField()
    meta = {"collection": "aaa"}


