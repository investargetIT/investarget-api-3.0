#coding=utf-8
import threading

from dataroom.models import dataroom_User_file
from msg.models import schedule
from proj.models import project, favoriteProject
from sourcetype.models import DataSource
from timeline.models import timelineTransationStatu
from usersys.models import MyUser, UserRelation, UserFriendship
from msg.views import saveMessage
from third.views.jpush import pushnotification
from third.views.submail import xsendSms, xsendEmail
from utils.util import logexcption, checkEmailTrue

sendEmail = True
sendSms = True
sendWebmsg = True
sendAppmsg = True




def getbase_domain(model):
    base_domain = None
    if isinstance(model, DataSource):
        base_domain = model.domain
    return base_domain

def getProjTitleWithSuperLink(proj,lang='cn'):
    if lang == 'cn':
        proj_superlink = '<a href=\'%s/app/projects/%s\'>%s</a>'%(getbase_domain(proj.datasource), proj.id, proj.projtitleC)
    else:
        proj_superlink = '<a href=\'%s/app/projects/%s\'>%s</a>'%(getbase_domain(proj.datasource), proj.id, proj.projtitleE)
    return proj_superlink

typelist = ['sms','app','email','webmsg']

favoriteTypeConf = {
# 1	系统推荐
# 3	交易师推荐
# 5	感兴趣
    '1':{
        'paths':['app','sms','webmsg','email'],
        'app':{
            'content' : '根据您的意向，系统向您推荐(%s)。',
            'platform' : 'ios',
            'bdage' : '1',
            'n_extras' : {},
        },
        'sms':{
            'projectsign' : 'lV0m62',
            'vars' : {},
        },
        'webmsg':{
            'content' : '根据您的意向，系统向您推荐(%s)。',
            'title' : '系统项目推荐',
            'messagetype' : 1,
        },
        'email':{
            'projectsign' : 'SRo1Y1',
            'vars' : {},
        },
    },
    '3':{
        'paths':['app','sms','webmsg','email'],
        'app':{
            'content' : '交易师推荐给您项目(%s)。',
            'platform' : 'ios',
            'bdage' : '1',
            'n_extras' : {},
        },
        'sms':{
            'projectsign' : 'S588p2',
            'vars' : {},
        },
        'webmsg':{
            'content' : '您的交易师%s推荐给您项目(%s)。',
            'title' : '交易师推荐给您项目',
            'messagetype' : 1,
        },
        'email':{
            'projectsign' : 'quyk52',
            'vars' : {},
        },
    },
    '5':{
        'paths':['app','sms','webmsg','email'],
        'app':{
            'content' : '有投资者对项目(%s)感兴趣',
            'platform' : 'ios',
            'bdage' : '1',
            'n_extras' : {},
        },
        'sms':{
            'projectsign' : 'JzW3h',
            'vars' : {},
        },
        'webmsg':{
            'content' : '您的投资者%s对项目(%s)感兴趣，请在48小时内联系投资者。',
            'title' : '您的投资者对项目感兴趣',
            'messagetype' : 1,
        },
        'email':{
            'projectsign' : 'LQrMB1',
            'vars' : {},
        },
    },
}



def sendmessage_favoriteproject(model,receiver,sender=None):
    """
    :param model: favoriteProject type
    :param receiver: myuser type
    :param types: list
    :param sender: myuser type
    :return: None
    """
    class sendmessage_favoriteprojectThread(threading.Thread):
        def __init__(self, model, receiver, sender=None):
            self.model = model
            self.receiver = receiver
            self.sender = sender
            threading.Thread.__init__(self)

        def run(self):
            receiver = self.receiver
            model = self.model
            sender = self.sender
            if isinstance(model, favoriteProject):
                if model.favoritetype_id != 4 and model.favoritetype_id != 2:
                    msgconfig = favoriteTypeConf[str(model.favoritetype_id)]
                    paths = msgconfig['paths']
                    if 'app' in paths and sendAppmsg:
                        try:
                            content = (msgconfig['app']['content']) % model.proj.projtitleC
                            receiver_alias = receiver.id
                            bdage = 1
                            n_extras = {}
                            pushnotification(content, receiver_alias, bdage, n_extras)
                        except Exception:
                            logexcption()
                    if 'email' in paths and sendEmail and checkEmailTrue(receiver.email):
                        try:
                            destination = receiver.email
                            projectsign = msgconfig['email']['projectsign']
                            if model.favoritetype_id in [3,5]:
                                vars = {'NameC': sender.usernameC, 'NameE': sender.usernameE, 'projectC': getProjTitleWithSuperLink(model.proj), 'projectE':getProjTitleWithSuperLink(model.proj,'en')}
                            else:
                                vars = {'projectC': getProjTitleWithSuperLink(model.proj), 'projectE':getProjTitleWithSuperLink(model.proj,'en')}
                            xsendEmail(destination, projectsign, vars)
                        except Exception:
                            logexcption()
                    if 'sms' in paths and sendSms:
                        try:
                            destination = receiver.mobile
                            projectsign = msgconfig['sms']['projectsign']
                            if model.favoritetype_id in [3,5]:
                                vars = {'user': sender.usernameC, 'project': model.proj.projtitleC, }
                            else:
                                vars = {'project':model.proj.projtitleC}
                            xsendSms(destination, projectsign, vars)
                        except Exception:
                            logexcption()
                    if 'webmsg' in paths and sendWebmsg:
                        try:
                            if model.favoritetype_id in [3,5]:
                                content = (msgconfig['webmsg']['content']) % (sender.usernameC, model.proj.projtitleC)
                            else:
                                content = (msgconfig['webmsg']['content']) % model.proj.projtitleC
                            title = msgconfig['webmsg']['title']
                            messagetype = msgconfig['webmsg']['messagetype']
                            saveMessage(content, messagetype, title, receiver, sender,modeltype='favoriteProject',sourceid=model.id)
                        except Exception:
                            logexcption()

    if checkReceiverToSendMsg(receiver):
        sendmessage_favoriteprojectThread(model,receiver,sender).start()

def sendmessage_traderadd(model,receiver,types,sender=None):
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
                if 'app' in types and sendAppmsg:
                    try:
                        content = '交易师已添加'
                        receiver_alias = receiver.id
                        bdage = 1
                        n_extras = {}
                        pushnotification(content, receiver_alias,  bdage, n_extras)
                    except Exception:
                        logexcption()
                if 'email' in types and sendEmail and checkEmailTrue(receiver.email):
                    try:
                        destination = receiver.email
                        projectsign = 'X6JEv3'
                        vars = {'nameC':model.traderuser.usernameC,'nameE':model.traderuser.usernameE}
                        xsendEmail(destination, projectsign, vars)
                    except Exception:
                        logexcption()
                if 'sms' in types and sendSms:
                    try:
                        destination = receiver.mobile
                        projectsign = 'pT0yA4'
                        vars = {'user': model.traderuser.usernameC}
                        xsendSms(destination, projectsign, vars)
                    except Exception:
                        logexcption()
                if 'webmsg' in types and sendWebmsg:
                    try:
                        content = '已为您添加交易师%s，感谢您的信任与支持' % model.traderuser.usernameC
                        title = '交易师已添加'
                        messagetype = 2
                        saveMessage(content, messagetype, title, receiver, sender,modeltype='UserRelation',sourceid=model.id)
                    except Exception:
                        logexcption()

    if checkReceiverToSendMsg(receiver):
        sendmessage_traderchangeThread(model,receiver,types,sender).start()

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
                if 'app' in types and sendAppmsg:
                    try:
                        if model.userstatus.id == 2:
                            content = '您在%s注册的%s账号已经通过审核，欢迎加入%s交易平台。'% (model.datasource.nameC, model.usernameC, model.datasource.nameC)
                        else:
                            content = '您在%s注册的%s账号%s，如有疑问，请咨询相关工作人员。'% (model.datasource.nameC, model.usernameC, model.userstatus.nameC)
                        receiver_alias = receiver.id
                        bdage = 1
                        n_extras = {}
                        pushnotification(content=content, receiver_alias=receiver_alias,  bdage=bdage, n_extras=n_extras)
                    except Exception:
                        logexcption()
                if 'email' in types and sendEmail and checkEmailTrue(receiver.email):
                    try:
                        if model.userstatus.id == 2:
                            destination = receiver.email
                            projectsign = 'uszOI1'
                            vars = {'nameC':model.usernameC,'nameE':model.usernameE}
                            xsendEmail(destination, projectsign, vars)
                        if model.userstatus.id == 3:
                            destination = receiver.email
                            projectsign = 'ZNRYV3'
                            vars = {'nameC':model.usernameC,'nameE':model.usernameE}
                            xsendEmail(destination, projectsign, vars)
                    except Exception:
                        logexcption()
                if 'sms' in types and sendSms:
                    try:
                        if model.userstatus.id == 2:
                            destination = receiver.mobile
                            projectsign = 'EXIDv1'
                            vars = {'user': model.usernameC}
                            xsendSms(destination, projectsign, vars)
                    except Exception:
                        logexcption()
                if 'webmsg' in types and sendWebmsg:
                    try:
                        if model.userstatus.id == 2:
                            content = '您在%s注册的%s账号已经通过审核，欢迎加入%s交易平台。'% (model.datasource.nameC, model.usernameC, model.datasource.nameC)
                            title = '账号状态更改'
                        else:
                            content = '您在%s注册的%s账号%s，如有疑问，请咨询相关工作人员。'% (model.datasource.nameC, model.usernameC, model.userstatus.nameC)
                            title = '账号状态更改'
                        messagetype = 3
                        saveMessage(content, messagetype, title, receiver, sender,modeltype='MyUser',sourceid=model.id)
                    except Exception:
                        logexcption()
    if checkReceiverToSendMsg(receiver):
        sendmessage_auditstatuchangeThread(model,receiver,types,sender).start()

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
                if 'app' in types and sendAppmsg:
                    try:
                        content = '我们已收到您提交的注册申请。我们将在24小时内与您取得联系，进行用户信息审核，并明确您的意向和需求。请您耐心等待！审核结果将通过邮件和短信通知您。感谢您对多维海拓的关注！'
                        receiver_alias = receiver.id
                        bdage = 1
                        n_extras = {}
                        pushnotification(content=content, receiver_alias=receiver_alias, bdage=bdage, n_extras=n_extras)
                    except Exception:
                        logexcption()
                if 'email' in types and sendEmail and checkEmailTrue(receiver.email):
                    try:
                        destination = receiver.email
                        projectsign = 'J6VK41'
                        vars = {}
                        xsendEmail(destination, projectsign, vars)
                    except Exception:
                        logexcption()
                if 'webmsg' in types and sendWebmsg:
                    try:
                        content = '我们已收到您提交的注册申请。我们将在24小时内与您取得联系，进行用户信息审核，并明确您的意向和需求。请您耐心等待！审核结果将通过邮件和短信通知您。感谢您对多维海拓的关注！'
                        title = '账号注册成功，审核工作会在24小时内开始。'
                        messagetype = 5
                        saveMessage(content, messagetype, title, receiver, sender,modeltype='MyUser',sourceid=model.id)
                    except Exception:
                        logexcption()

    if checkReceiverToSendMsg(receiver):
        sendmessage_userregisterThread(model,receiver,types,sender).start()



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
                if 'app' in types and sendAppmsg:
                    try:
                        content = '您的项目%s时间轴状态已更新，点击查看最新状态'%model.timeline.proj.projtitleC
                        receiver_alias = receiver.id
                        bdage = 1
                        n_extras = {}
                        pushnotification(content, receiver_alias, bdage, n_extras)
                    except Exception:
                        logexcption()
                if 'email' in types and sendEmail and checkEmailTrue(receiver.email):
                    try:
                        destination = receiver.email
                        projectsign = 'LkZix2'
                        vars = {'projectC': getProjTitleWithSuperLink(model.timeline.proj),'projectE': getProjTitleWithSuperLink(model.timeline.proj,'en')}
                        xsendEmail(destination, projectsign, vars)
                    except Exception:
                        logexcption()
                if 'sms' in types and sendSms:
                    try:
                        destination = receiver.mobile
                        projectsign = 'tNEV93'
                        vars = {'project': model.timeline.proj.projtitleC}
                        xsendSms(destination, projectsign, vars)
                    except Exception:
                        logexcption()
                if 'webmsg' in types and sendWebmsg:
                    try:
                        content = '您的项目%s时间轴状态已更新，点击查看最新状态'%model.timeline.proj.projtitleC
                        title = '时间轴状态更新'
                        messagetype = 6
                        saveMessage(content, messagetype, title, receiver, sender,modeltype='timelineTransationStatu',sourceid=model.id)
                    except Exception:
                        logexcption()

    if checkReceiverToSendMsg(receiver):
        sendmessage_timelineauditstatuchangeThread(model,receiver,types,sender).start()

def sendmessage_dataroomfileupdate(model,receiver,types,sender=None):
    """
    :param model: dataroom_User_file type
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
            if isinstance(model, dataroom_User_file):
                if 'app' in types and sendAppmsg:
                    try:
                        content = 'DataRoom有文件更新，点击查看详情'
                        receiver_alias = receiver.id
                        bdage = 1
                        n_extras = {}
                        pushnotification(content, receiver_alias, bdage, n_extras)
                    except Exception:
                        logexcption()
                if 'email' in types and sendEmail and checkEmailTrue(receiver.email):
                    try:
                        destination = receiver.email
                        projectsign = 'umZlP3'
                        vars = {'projectC': getProjTitleWithSuperLink(model.dataroom.proj), 'projectE': getProjTitleWithSuperLink(model.dataroom.proj, 'en')}
                        xsendEmail(destination, projectsign, vars)
                    except Exception:
                        logexcption()
                if 'sms' in types and sendSms:
                    try:
                        destination = receiver.mobile
                        projectsign = 'huvrW4'
                        vars = {'project': model.dataroom.proj.projtitleC}
                        xsendSms(destination, projectsign, vars)
                    except Exception:
                        logexcption()
                if 'webmsg' in types and sendWebmsg:
                    try:
                        content = '您的项目%s，DataRoom有文件更新，请登录后查看'%model.dataroom.proj.projtitleC
                        title = 'DataRoom有文件更新，点击查看详情'
                        messagetype = 7
                        saveMessage(content, messagetype, title, receiver, sender,modeltype='dataroom_User_file',sourceid=model.id)
                    except Exception:
                        logexcption()

    if checkReceiverToSendMsg(receiver):
        sendmessage_dataroomfileupdateThread(model,receiver,types,sender).start()

def sendmessage_projectpublish(model, receiver, types, sender=None):
    """
        :param model: project type
        :param receiver: myuser type
        :param types: list
        :param sender: myuser type
        :return: None
        """

    class sendmessage_projectpublishThread(threading.Thread):
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
                if 'email' in types and sendEmail and checkEmailTrue(receiver.email):
                    try:
                        destination = receiver.email
                        projectsign = 'IszFR1'
                        vars = {'projectC': getProjTitleWithSuperLink(model), 'projectE': getProjTitleWithSuperLink(model, 'en')}
                        xsendEmail(destination, projectsign, vars)
                    except Exception:
                        logexcption()
                if 'webmsg' in types and sendWebmsg:
                    try:
                        content = '您的项目%s，状态变更为已发布。' % model.dataroom.proj.projtitleC
                        title = '项目状态变更'
                        messagetype = 8
                        saveMessage(content, messagetype, title, receiver, sender,modeltype='project',sourceid=model.id)
                    except Exception:
                        logexcption()

    if checkReceiverToSendMsg(receiver):
        sendmessage_projectpublishThread(model,receiver,types,sender).start()

def sendmessage_usermakefriends(model,receiver,types,sender=None):
    """
    :param model: UserFriendship type
    :param receiver: myuser type
    :param types: list
    :param sender: myuser type
    :return: None
    """
    class sendmessage_usermakefriendsThread(threading.Thread):
        def __init__(self, model, receiver, types, sender = None):
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
                if 'app' in types and sendAppmsg:
                    try:
                        content = '您有一个好友添加申请'
                        receiver_alias = receiver.id
                        bdage = 1
                        n_extras = {}
                        pushnotification(content, receiver_alias, bdage, n_extras)
                    except Exception:
                        logexcption()
                if 'webmsg' in types and sendWebmsg:
                    try:
                        content = '您有一个好友添加申请'
                        title = '好友添加申请'
                        messagetype = 9
                        saveMessage(content, messagetype, title, receiver, sender,modeltype='UserFriendship',sourceid=model.id)
                    except Exception:
                        logexcption()

    if checkReceiverToSendMsg(receiver):
        sendmessage_usermakefriendsThread(model,receiver,types,sender).start()

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
                if 'app' in types and sendAppmsg:
                    try:
                        content = '您有一个时间轴提醒到期'
                        receiver_alias = receiver.id
                        bdage = 1
                        n_extras = {}
                        pushnotification(content, receiver_alias, bdage, n_extras)
                    except Exception:
                        logexcption()
                if 'webmsg' in types and sendWebmsg:
                    try:
                        content = '您有一个时间轴提醒到期'
                        title = '时间轴到期提醒'
                        messagetype = 10
                        saveMessage(content, messagetype, title, receiver, sender,modeltype='timelineTransationStatu',sourceid=model.id)
                    except Exception:
                        logexcption()

    if checkReceiverToSendMsg(receiver):
        sendmessage_timelinealertcycleexpireThread(model,receiver,types,sender).start()

def sendmessage_schedulemsg(model,receiver,types,sender=None):
    """
    :param model: UserFriendship type
    :param receiver: myuser type
    :param types: list
    :param sender: myuser type
    :return: None
    """
    class sendmessage_schedulemsgThread(threading.Thread):
        def __init__(self, model, receiver, types, sender = None):
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
            if isinstance(model, schedule):
                if 'app' in types and sendAppmsg:
                    try:
                        content = '您有一个日程今天到期'
                        receiver_alias = receiver.id
                        bdage = 1
                        n_extras = {}
                        pushnotification(content, receiver_alias, bdage, n_extras)
                    except Exception:
                        logexcption()
                if 'webmsg' in types and sendWebmsg:
                    try:
                        content = '您有一个日程今天到期'
                        title = '日程到期'
                        messagetype = 11
                        saveMessage(content, messagetype, title, receiver, sender,modeltype='schedule',sourceid=model.id)
                    except Exception:
                        logexcption()

    if checkReceiverToSendMsg(receiver):
        sendmessage_schedulemsgThread(model,receiver,types,sender).start()


def sendmessage_orgBDMessage(model,receiver,types,sender=None):
    """
    :param model: UserFriendship type
    :param receiver: myuser type
    :param types: list
    :param sender: myuser type
    :return: None
    """
    class sendmessage_orgBDMessageThread(threading.Thread):
        def __init__(self, model, receiver, types, sender = None):
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
            if 'app' in types and sendAppmsg:
                try:
                    content = '您有一个新机构BD任务'
                    receiver_alias = receiver.id
                    bdage = 1
                    n_extras = {}
                    pushnotification(content, receiver_alias, bdage, n_extras)
                except Exception:
                    logexcption()
            if 'webmsg' in types and sendWebmsg:
                try:
                    content = '您有一个新机构BD任务'
                    title = '机构BD'
                    messagetype = 12
                    saveMessage(content, messagetype, title, receiver, sender, modeltype='OrgBD', sourceid=model.id)
                except Exception:
                    logexcption()
            if 'sms' in types and sendSms:
                try:
                    destination = receiver.mobile
                    projectsign = 'M2d4Q3'
                    vars = {}
                    xsendSms(destination, projectsign, vars)
                except Exception:
                    logexcption()


    # if checkReceiverToSendMsg(receiver):
    #     sendmessage_orgBDMessageThread(model,receiver,types,sender).start()


# 判断是否发送消息
def checkReceiverToSendMsg(receiver):
    if receiver is not None:
        if isinstance(receiver, MyUser):
            if getattr(receiver, 'datasource_id') == 1 and receiver.is_active:
                return True
    return False