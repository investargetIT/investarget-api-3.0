#coding=utf-8
import threading

from dataroom.models import dataroomdirectoryorfile
from proj.models import project, favoriteProject
from timeline.models import timelineTransationStatu
from usersys.models import MyUser, UserRelation, UserFriendship
from org.models import organization
from msg.views import saveMessage
from third.views.jpush import pushnotification
from third.views.submail import xsendSms, xsendEmail

typelist = ['sms','app','email','webmsg']


messageconfig = {
    'favoriteproject':{
        'modeltype':favoriteProject,
        'app':{
            'content' : '',
            'platform' : 'ios',
            'bdage' : '1',
            'n_extras' : {},
        },
        'sms':{
            'projectsign' : '',
            'vars' : {},
        },
        'webmsg':{
            'content' : '',
            'title' : '',
            'messagetype' : 1,
        },
        'email':{
            'projectsign' : '',
            'vars' : {},
        },
    },
    'traderchange':{
        'modeltype':UserRelation,
        'app':{
            'content' : '',
            'platform' : 'ios',
            'bdage' : '1',
            'n_extras' : {},
        },
        'sms':{
            'projectsign' : '',
            'vars' : {},
        },
        'webmsg':{
            'content' : '',
            'title' : '',
            'messagetype' : 1,
        },
        'email':{
            'projectsign' : '',
            'vars' : {},
        },
    },
    'userauditstatuschange':{
    'modeltype':MyUser,
        'app':{
            'content' : '',
            'platform' : 'ios',
            'bdage' : '1',
            'n_extras' : {},
        },
        'sms':{
            'projectsign' : '',
            'vars' : {},
        },
        'webmsg':{
            'content' : '',
            'title' : '',
            'messagetype' : 1,
        },
        'email':{
            'projectsign' : '',
            'vars' : {},
        },
    },
    'userregister':{
        'modeltype':MyUser,
        'app':{
            'content' : '',
            'platform' : 'ios',
            'bdage' : '1',
            'n_extras' : {},
        },
        'sms':{
            'projectsign' : '',
            'vars' : {},
        },
        'webmsg':{
            'content' : '',
            'title' : '',
            'messagetype' : 1,
        },
        'email':{
            'projectsign' : '',
            'vars' : {},
        },
    },
    'projectauditstatuschange':{
        'modeltype':project,
        'app':{
            'content' : '',
            'platform' : 'ios',
            'bdage' : '1',
            'n_extras' : {},
        },
        'sms':{
            'projectsign' : '',
            'vars' : {},
        },
        'webmsg':{
            'content' : '',
            'title' : '',
            'messagetype' : 1,
        },
        'email':{
            'projectsign' : '',
            'vars' : {},
        },
    },
    'orgauditstatuschange':{
        'modeltype':organization,
        'app':{
            'content' : '',
            'platform' : 'ios',
            'bdage' : '1',
            'n_extras' : {},
        },
        'sms':{
            'projectsign' : '',
            'vars' : {},
        },
        'webmsg':{
            'content' : '',
            'title' : '',
            'messagetype' : 1,
        },
        'email':{
            'projectsign' : '',
            'vars' : {},
        },
    },
    'timelinestatuschange':{
        'modeltype':timelineTransationStatu,
        'app':{
            'content' : '',
            'platform' : 'ios',
            'bdage' : '1',
            'n_extras' : {},
        },
        'sms':{
            'projectsign' : '',
            'vars' : {},
        },
        'webmsg':{
            'content' : '',
            'title' : '',
            'messagetype' : 1,
        },
        'email':{
            'projectsign' : '',
            'vars' : {},
        },
    },
    'timelinealertcycleexpire':{
        'modeltype':timelineTransationStatu,
        'app':{
            'content' : '',
            'platform' : 'ios',
            'bdage' : '1',
            'n_extras' : {},
        },
        'sms':{
            'projectsign' : '',
            'vars' : {},
        },
        'webmsg':{
            'content' : '',
            'title' : '',
            'messagetype' : 1,
        },
        'email':{
            'projectsign' : '',
            'vars' : {},
        },
    },
    'dataroomfileupdate':{
        'modeltype':dataroomdirectoryorfile,
        'app':{
            'content' : '',
            'platform' : 'ios',
            'bdage' : '1',
            'n_extras' : {},
        },
        'sms':{
            'projectsign' : '',
            'vars' : {},
        },
        'webmsg':{
            'content' : '',
            'title' : '',
            'messagetype' : 1,
        },
        'email':{
            'projectsign' : '',
            'vars' : {},
        },
    },
    'usermakefriend':{
        'modeltype':UserFriendship,
        'app':{
            'content' : '',
            'platform' : 'ios',
            'bdage' : '1',
            'n_extras' : {},
        },
        'sms':{
            'projectsign' : '',
            'vars' : {},
        },
        'webmsg':{
            'content' : '',
            'title' : '',
            'messagetype' : 1,
        },
        'email':{
            'projectsign' : '',
            'vars' : {},
        },
    },
}

def sendmessage_withtypes(configtype,model,receiver,types,sender=None):
    """
    :param configtype: messageconfig
    :param model: favoriteProject type
    :param receiver: myuser type
    :param types: list
    :param sender: myuser type
    :return: None
    """
    class sendmessageThread(threading.Thread):
        def __init__(self, configtype, model, receiver, types, sender=None):
            self.configtype = configtype
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
            if hasattr(messageconfig,configtype):
                data = messageconfig[configtype]
                if isinstance(model, data['modeltype']):
                    if 'app' in types:
                        appdata = data['app']
                        content = appdata['content']
                        receiver_alias = receiver.usercode
                        platform = appdata['platform']
                        bdage = appdata['bdage']
                        n_extras = appdata['n_extras']
                        pushnotification(content, receiver_alias, platform, bdage, n_extras)
                    if 'email' in types:
                        emaildata = data['email']
                        destination = receiver.email
                        projectsign = emaildata['projectsign']
                        vars = emaildata['vars']
                        xsendEmail(destination, projectsign, vars)
                    if 'sms' in types:
                        smsdata = data['sms']
                        destination = receiver.email
                        projectsign = smsdata['projectsign']
                        vars = smsdata['vars']
                        xsendSms(destination, projectsign, vars)
                    if 'webmsg' in types:
                        webmsgdata = data['webmsg']
                        content = webmsgdata['content']
                        title = webmsgdata['title']
                        messagetype = webmsgdata['messagetype']
                        saveMessage(content, messagetype, title, receiver, sender)
            else:
                print u'%s not found'%configtype
                pass
    sendmessageThread(model,receiver,types,sender).start()




def sendmessage_favoriteproject(model,receiver,types,sender=None):
    """
    :param model: favoriteProject type
    :param receiver: myuser type
    :param types: list
    :param sender: myuser type
    :return: None
    """
    class sendmessage_favoriteprojectThread(threading.Thread):
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

    # sendmessage_favoriteprojectThread(model,receiver,types,sender).start()

def sendmessage_traderchange(model,receiver,types,sender=None):
    """
    :param model: UserRelation type
    :param receiver: myuser type
    :param types: list
    :param sender: myuser type
    :return: None
    """
    class sendmessage_traderchangeThread(threading.Thread):
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
                    content = '交易师已更换'
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

    # sendmessage_traderchangeThread(model,receiver,types,sender).start()

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
                    content = '您的账号状态已经改为\'%s\''%model.userstatu.nameC
                    receiver_alias = receiver.mobile
                    platform = 'ios'
                    bdage = 1
                    n_extras = {}
                    pushnotification(content=content, receiver_alias=receiver_alias, platform=platform, bdage=bdage, n_extras=n_extras)
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
                    content = '您的账号状态已经改为\'%s\'，如有疑问，请咨询相关工作人员。'%model.userstatu.nameC
                    title = '您的账号状态已经改为\'%s\''%model.userstatu.nameC
                    messagetype = 1
                    saveMessage(content, messagetype, title, receiver, sender)

    # sendmessage_auditstatuchangeThread(model,receiver,types,sender).start()

def sendmessage_userregister(model,receiver,types,sender=None):
    """
    :param model: MyUser type
    :param receiver: myuser type
    :param types: list
    :param sender: myuser type
    :return: None
    """
    class sendmessage_userregisterThread(threading.Thread):
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
                    content = '我们已收到您提交的注册申请。我们将在24小时内与您取得联系，进行用户信息审核，并明确您的意向和需求。请您耐心等待！审核结果将通过邮件和短信通知您。感谢您对多维海拓的关注！'
                    receiver_alias = receiver.mobile
                    platform = 'ios'
                    bdage = 1
                    n_extras = {}
                    pushnotification(content=content, receiver_alias=receiver_alias, platform=platform, bdage=bdage, n_extras=n_extras)
                if 'email' in types:
                    destination = receiver.email
                    projectsign = 'J6VK41'
                    vars = {}
                    xsendEmail(destination, projectsign, vars)
                if 'sms' in types:
                    destination = receiver.mobile
                    projectsign = 'WzSYg'
                    vars = {'code': 'sss', 'time': '10'}
                    xsendSms(destination, projectsign, vars)
                if 'webmsg' in types:
                    content = '您的账号状态已经改为\'%s\'，如有疑问，请咨询相关工作人员。'%model.userstatu.nameC
                    title = '您的账号状态已经改为\'%s\''%model.userstatu.nameC
                    messagetype = 1
                    saveMessage(content, messagetype, title, receiver, sender)

    # sendmessage_userregisterThread(model,receiver,types,sender).start()

def sendmessage_projectauditstatuchange(model,receiver,types,sender=None):
    """
    :param model: project type
    :param receiver: myuser type
    :param types: list
    :param sender: myuser type
    :return: None
    """
    class sendmessage_projectauditstatuchangeThread(threading.Thread):
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
    # sendmessage_projectauditstatuchangeThread(model,receiver,types,sender).start()

def sendmessage_orgauditstatuchange(model,receiver,types,sender=None):
    """
    :param model: organization type
    :param receiver: myuser type
    :param types: list
    :param sender: myuser type
    :return: None
    """
    class sendmessage_orgauditstatuchangeThread(threading.Thread):
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
    # sendmessage_orgauditstatuchangeThread(model,receiver,types,sender).start()

def sendmessage_timelineauditstatuchange(model,receiver,types,sender=None):
    """
    :param model: timelineTransationStatu type
    :param receiver: myuser type
    :param types: list
    :param sender: myuser type
    :return: None
    """
    class sendmessage_timelineauditstatuchangeThread(threading.Thread):
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
    # sendmessage_timelineauditstatuchangeThread(model,receiver,types,sender).start()

def sendmessage_timelinealertcycleexpire(model,receiver,types,sender=None):
    """
    :param model: timelineTransationStatu type
    :param receiver: myuser type
    :param types: list
    :param sender: myuser type
    :return: None
    """
    class sendmessage_timelinealertcycleexpireThread(threading.Thread):
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

    # sendmessage_timelinealertcycleexpireThread(model,receiver,types,sender).start()

def sendmessage_dataroomfileupdate(model,receiver,types,sender=None):
    """
    :param model: dataroomdirectoryorfile type
    :param receiver: myuser type
    :param types: list
    :param sender: myuser type
    :return: None
    """
    class sendmessage_dataroomfileupdateThread(threading.Thread):
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

    # sendmessage_dataroomfileupdateThread(model,receiver,types,sender).start()

def sendmessage_usermakefriends(model,receiver,types,sender=None):
    """
    :param model: dataroomdirectoryorfile type
    :param receiver: myuser type
    :param types: list
    :param sender: myuser type
    :return: None
    """
    class sendmessage_usermakefriendsThread(threading.Thread):
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
            if isinstance(model, UserFriendship):
                if 'app' in types:
                    content = 'test 3.0'
                    receiver_alias = receiver.mobile
                    platform = 'ios'
                    bdage = 1
                    n_extras = {}
                    pushnotification(content, receiver_alias, platform, bdage, n_extras)
                if 'email' in types:
                    destination = receiver.email
                    projectsign = 'J6VK41'
                    vars = {}
                    xsendEmail(destination, projectsign, vars)
                if 'sms' in types:
                    destination = receiver.mobile
                    projectsign = 'WzSYg'
                    vars = {'code': 'sss', 'time': '10'}
                    xsendSms(destination, projectsign, vars)
                if 'webmsg' in types:
                    content = 'test 3.0 content'
                    title = 'test 3.0'
                    messagetype = 1
                    saveMessage(content, messagetype, title, receiver, sender)
    # sendmessage_usermakefriendsThread(model,receiver,types,sender).start()
