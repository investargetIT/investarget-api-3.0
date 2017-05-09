#coding=utf-8
import threading

from dataroom.models import dataroomdirectoryorfile
from proj.models import project, favoriteProject
from timeline.models import timelineTransationStatu
from usersys.models import MyUser, UserRelation
from org.models import organization
from msg.views import saveMessage
from third.views.jpush import pushnotification
from third.views.submail import xsendSms, xsendEmail

typelist = ['sms','app','email','webmsg']

def sendmessage_favoriteproject(model,receiver,types,sender=None):
    """
    :param model: favoriteProject type
    :param receiver: myuser type
    :param types: list
    :param sender: myuser type
    :return: None
    """

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
            if isinstance(model, favoriteProject):
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

    sendmessage_auditstatuchangeThread(model,receiver,types,sender).start()

def sendmessage_traderchange(model,receiver,types,sender=None):
    """
    :param model: UserRelation type
    :param receiver: myuser type
    :param types: list
    :param sender: myuser type
    :return: None
    """
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
            if isinstance(model, UserRelation):
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

    sendmessage_auditstatuchangeThread(model,receiver,types,sender).start()

def sendmessage_userauditstatuchange(model,receiver,types,sender=None):
    """
    :param model: MyUser type
    :param receiver: myuser type
    :param types: list
    :param sender: myuser type
    :return: None
    """
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

    sendmessage_auditstatuchangeThread(model,receiver,types,sender).start()

def sendmessage_projectauditstatuchange(model,receiver,types,sender=None):
    """
    :param model: project type
    :param receiver: myuser type
    :param types: list
    :param sender: myuser type
    :return: None
    """
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
            if isinstance(model, project):
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
    sendmessage_auditstatuchangeThread(model,receiver,types,sender).start()

def sendmessage_orgauditstatuchange(model,receiver,types,sender=None):
    """
    :param model: organization type
    :param receiver: myuser type
    :param types: list
    :param sender: myuser type
    :return: None
    """
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
            if isinstance(model, organization):
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
    sendmessage_auditstatuchangeThread(model,receiver,types,sender).start()

def sendmessage_timelineauditstatuchange(model,receiver,types,sender=None):
    """
    :param model: timelineTransationStatu type
    :param receiver: myuser type
    :param types: list
    :param sender: myuser type
    :return: None
    """
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
            if isinstance(model, timelineTransationStatu):
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
    sendmessage_auditstatuchangeThread(model,receiver,types,sender).start()

def sendmessage_timelinealertcycleexpire(model,receiver,types,sender=None):
    """
    :param model: timelineTransationStatu type
    :param receiver: myuser type
    :param types: list
    :param sender: myuser type
    :return: None
    """
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
            if isinstance(model, timelineTransationStatu):
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

    sendmessage_auditstatuchangeThread(model,receiver,types,sender).start()

def sendmessage_dataroomfileupdate(model,receiver,types,sender=None):
    """
    :param model: dataroomdirectoryorfile type
    :param receiver: myuser type
    :param types: list
    :param sender: myuser type
    :return: None
    """
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
            if isinstance(model, dataroomdirectoryorfile):
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

    sendmessage_auditstatuchangeThread(model,receiver,types,sender).start()

