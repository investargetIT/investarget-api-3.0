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




def sendmessage_favoriteproject(projfavormodel,receiver,types,sender=None):
    pass


def sendmessage_traderchange(relationmodel,receiver,types,sender=None):
    pass




def sendmessage_auditstatuchange(model,receiver,types,sender=None):
    class sendmessage_auditstatuchangeThread(threading.Thread):
        def __init__(self, model, receiver, types, sender=None):
            self.model = model
            self.receiver = receiver
            self.types = types
            self.sender = sender
            threading.Thread.__init__(self)

        def run(self):
            types = self.types
            receiver = self.receiver
            model = self.model
            sender = self.sender
            if isinstance(model, MyUser):
                if 'app' in types:
                    content = ''
                    receiver_alias = receiver.usercode
                    platform = 'ios'
                    bdage = 1
                    n_extras = {}
                    pushnotification(content, receiver_alias, platform, bdage, n_extras)
                if 'email' in types:
                    destination = receiver.email
                    projectsign = ''
                    vars = {}
                    xsendEmail(destination, projectsign, vars)
                if 'sms' in types:
                    destination = receiver.mobile
                    projectsign = 'WzSYg'
                    vars = {'code': 'sss', 'time': '10'}
                    xsendSms(destination, projectsign, vars)
                if 'webmsg' in types:
                    content = ''
                    title = ''
                    messagetype = 1
                    saveMessage(content, messagetype, title, receiver, sender)
            elif isinstance(model, organization):
                pass
            elif isinstance(model, project):
                pass
            elif isinstance(model, timelineTransationStatu):
                pass
    sendmessage_auditstatuchangeThread(model,receiver,types,sender).start()

def sendmessage_timelinealertcycleexpire(model,receiver,types,sender=None):
    pass

def sendmessage_dataroomfileupdate(model,receiver,types,sender=None):
    pass

