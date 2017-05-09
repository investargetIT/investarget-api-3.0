#coding=utf-8
import threading

from proj.models import project
from timeline.models import timelineTransationStatu
from usersys.models import MyUser
from org.models import organization
from msg.views import saveMessage
from third.views.jpush import pushnotification
from third.views.submail import xsendSms, xsendEmail

typelist = ['app','email','sms','webmsg']

#模板ID（短信/邮件）
PRODUCT_SIGNS = {}



class AppThread(threading.Thread):
    def __init__(self,content, receiver_alias, platform, bdage, n_extras):
        self.content = content
        self.receiver_alias = receiver_alias
        self.platform = platform
        self.bdage = bdage
        self.n_extras = n_extras
        threading.Thread.__init__(self)
    def run (self):
        data_dict = {
            'receiver_alias': self.receiver_alias,
            'content': self.content,
            'platform': self.platform,
            'bdage': self.bdage,
            'n_extras': self.n_extras,
        }
        return pushnotification(data_dict)

class EmailThread(threading.Thread):
    def __init__(self,destination,projectsign,vars=None):
        self.destination = destination
        self.projectsign = projectsign
        self.vars = vars
        threading.Thread.__init__(self)
    def run (self):
        return xsendEmail(self.destination,self.projectsign,self.vars)

class SmsThread(threading.Thread):
    def __init__(self,destination,projectsign,vars=None):
        self.destination = destination
        self.projectsign = projectsign
        self.vars = vars
        threading.Thread.__init__(self)
    def run (self):
        return xsendSms(self.destination,self.projectsign,self.vars)


class WebMsgThread(threading.Thread):
    def __init__(self,content, messagetype, title, receiver, sender):
        self.content = content
        self.messagetype = messagetype
        self.title = title
        self.receiver = receiver
        self.sender = sender
        threading.Thread.__init__(self)
    def run (self):
        return saveMessage(self.content, self.messagetype, self.title, self.receiver, self.sender)


def sendmessage_favoriteproject(projfavormodel,receiver,types,sender=None):
    pass


def sendmessage_traderchange(relationmodel,receiver,types,sender=None):
    pass

def sendmessage_auditstatuchange(model,receiver,types,sender=None):
    if isinstance(model, MyUser):
        if 'app' in types:
            content = ''
            receiver_alias = receiver.usercode
            platform = 'ios'
            bdage = 1
            n_extras = {}
            AppThread(content, receiver_alias, platform, bdage, n_extras).start()
        if 'email' in types:
            destination = receiver.email
            projectsign = ''
            vars = {}
            EmailThread(destination, projectsign, vars).start()
        if 'sms' in types:
            destination = receiver.mobile
            projectsign = 'WzSYg'
            vars = {'code':'sss','time':'10'}
            SmsThread(destination, projectsign, vars).start()
        if 'webmsg' in types:
            content = ''
            title = ''
            messagetype = 1
            WebMsgThread(content, messagetype, title, receiver, sender).start()
    elif isinstance(model, organization):
        pass
    elif isinstance(model, project):
        pass
    elif isinstance(model, timelineTransationStatu):
        pass

def sendmessage_timelinealertcycleexpire(model,receiver,types,sender=None):
    pass

def sendmessage_dataroomfileupdate(model,receiver,types,sender=None):
    pass

