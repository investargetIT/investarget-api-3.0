#coding=utf-8
import json
from SUBMAIL_PYTHON_SDK_MAIL_AND_MESSAGE_WITH_ADDRESSBOOK.app_configs import MAIL_CONFIGS, MESSAGE_CONFIGS
from SUBMAIL_PYTHON_SDK_MAIL_AND_MESSAGE_WITH_ADDRESSBOOK.mail_xsend import MAILXsend
from SUBMAIL_PYTHON_SDK_MAIL_AND_MESSAGE_WITH_ADDRESSBOOK.message_xsend import MESSAGEXsend


def sendEmail(destination,content,title):


    '''
    init MESSAGEXsend class
    '''
    submail = MAILXsend(MAIL_CONFIGS)

    '''
    Optional para
    The First para: recipient email address
    The second para: recipient name(optional)
    @Multi-para
    '''
    submail.add_to('leo@submail.cn', 'leo')

    '''
    Optional para
    set addressbook sign : Optional
    add addressbook contacts to Multi-Recipients
    @Multi-para
    '''
    # submail.add_address_book('subscribe')

    '''
    Optional para
    set sender address and name
    The First para: sender email address
    The second para: sender display name (optional)
    '''
    # submail.set_sender('no-reply@submail.cn','SUBMAIL')

    '''
    Optional para
    set reply address
    '''
    # submail.set_reply('service@submail.cn')

    '''
    Optional para
    set email subject
    '''
    # submail.set_subject('test SDK')

    '''
    Required para
    set project sign
    '''
    submail.set_project('uigGk1')

    '''
    Optional para
    submail email text content filter
    @Multi-para
    '''
    submail.add_var('name', 'leo')
    submail.add_var('age', '32')

    '''
    Optional para
    submail email link content filter
    @Multi-para
    '''
    submail.add_link('developer', 'http://submail.cn/chs/developer')
    submail.add_link('store', 'http://submail.cn/chs/store')

    '''
    Optional para
    email headers
    @Multi-para
    '''
    submail.add_header('X-Accept', 'zh-cn')
    submail.add_header('X-Mailer', 'leo App')
    submail.xsend()
def sendSms(destination,content,title):
    submail = MESSAGEXsend(MESSAGE_CONFIGS)

    '''
    Optional para
    recipient cell phone number
    @Multi-para
    '''
    submail.add_to('18616761881')

    '''
    Optional para
    set addressbook sign : Optional
    add addressbook contacts to Multi-Recipients
    @Multi-para
    '''
    # submail.add_address_book('subscribe')

    '''
    Required para
    set message project sign
    '''
    submail.set_project('kZ9Ky3')

    '''
    Optional para
    submail email text content filter
    @Multi-para
    '''
    submail.add_var('code', '198276')
    submail.xsend()

def sendInternationalsms(destination,content,title):
    pass