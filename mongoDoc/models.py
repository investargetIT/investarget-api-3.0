#coding:utf-8
from __future__ import unicode_literals

import datetime
from mongoengine import *
from invest.settings import groupemailMongoTableName, chatMessagegMongoTableName, projectDataMongoTableName, \
    mergeandfinanceeventMongoTableName, com_catMongoTableName, projremarkMongoTableName, wxchatdataMongoTableName
from utils.customClass import InvestError


class CompanyCatData(Document):
    p_cat_id = StringField(null=True)
    p_cat_name = StringField(null=True)
    cat_id = StringField(null=True)
    cat_name= StringField(null=True)
    meta = {"collection": com_catMongoTableName}


class ProjectData(Document):
    com_id = StringField()      #公司id
    com_name = StringField()   #公司名称
    com_status = StringField(null=True)  #公司运营状态
    com_scale= StringField(null=True)    #公司规模
    invse_round_id = StringField(null=True)  #公司获投状态
    com_cat_name = StringField(null=True)  #行业
    com_sub_cat_name = StringField(null=True) #子行业
    com_born_date = StringField(null=True)   #成立日期
    invse_detail_money = StringField(null=True)  #最新融资金额
    guzhi = StringField(null=True)          #估值
    invse_date = StringField(null=True)   #最新融资日期
    com_logo_archive = StringField(null=True)   #公司logo
    com_fund_needs_name = StringField(null=True) #融资需求
    com_des = StringField(null=True)   #公司介绍
    invse_total_money = StringField(null=True)  #融资总额
    com_addr = StringField(null=True)   #公司所在地
    meta = {"collection": projectDataMongoTableName}

    def save(self, force_insert=False, validate=True, clean=True,
             write_concern=None, cascade=None, cascade_kwargs=None,
             _refs=None, save_condition=None, signal_kwargs=None, **kwargs):
        if len(ProjectData.objects.filter(com_id=self.com_id)) > 0:
            raise InvestError(8001,msg='数据重复')
        super(ProjectData,self).save(force_insert,validate,clean,write_concern,cascade,cascade_kwargs,_refs,save_condition,signal_kwargs,**kwargs)

class MergeFinanceData(Document):

    com_id = StringField(null=True)  #公司id
    com_logo = StringField(null=True)  # 公司logo
    com_name = StringField(null=True)  # 公司名称
    currency= StringField(null=True)    #货币类型
    money = StringField(null=True)  #金额
    date = StringField(null=True)  #日期

    invsest_with = ListField(null=True)  # 投资方
    invse_id = StringField(null=True)  # 投资事件id
    round = StringField(null=True)   #公司融资轮次

    merger_equity_ratio = StringField(null=True)  #股权比例
    merger_with = StringField(null=True)   #并购方名称
    merger_id = StringField(null=True)   #并购事件id

    investormerge = IntField(default=1)   #并购事件（2）or 投资事件（1）
    meta = {"collection": mergeandfinanceeventMongoTableName}

    def save(self, force_insert=False, validate=True, clean=True,
             write_concern=None, cascade=None, cascade_kwargs=None,
             _refs=None, save_condition=None, signal_kwargs=None, **kwargs):
        if self.investormerge == 1:
            if len(MergeFinanceData.objects.filter(invse_id=self.invse_id)) > 0:
                raise InvestError(8001)
        elif self.investormerge == 2:
            if len(MergeFinanceData.objects.filter(merger_id=self.merger_id)) > 0:
                raise InvestError(8001)
        else:
            raise InvestError(8001,msg='未知的类型')
        super(MergeFinanceData,self).save(force_insert,validate,clean,write_concern,cascade,cascade_kwargs,_refs,save_condition,signal_kwargs,**kwargs)

class ProjRemark(Document):
    com_id = StringField(null=True)  # 公司id
    com_name = StringField(null=True)  # 公司名称
    remark = StringField(null=True)
    createuser_id = IntField()
    datasource = IntField()
    date = DateTimeField(default=datetime.datetime.now())
    meta = {"collection": projremarkMongoTableName}


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

class WXChatdata(Document):
    content = StringField()
    createtime = DateTimeField()
    name = StringField()
    group_name = StringField()
    isShow = BooleanField(default=True)
    meta = {"collection": wxchatdataMongoTableName}
