#coding=utf-8
import json
import traceback

from SUBMAIL_PYTHON_SDK_MAIL_AND_MESSAGE_WITH_ADDRESSBOOK.app_configs import MAIL_CONFIGS, MESSAGE_CONFIGS, \
    INTERNATIONALMESSAGE_CONFIGS
from SUBMAIL_PYTHON_SDK_MAIL_AND_MESSAGE_WITH_ADDRESSBOOK.mail_xsend import MAILXsend
from SUBMAIL_PYTHON_SDK_MAIL_AND_MESSAGE_WITH_ADDRESSBOOK.message_xsend import MESSAGEXsend
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

from third.models import MobileAuthCode
from utils.myClass import JSONResponse, InvestError
from utils.util import SuccessResponse, catchexcption, ExceptionResponse, InvestErrorResponse

'''
（海拓）注册短信验证码模板
'''
SMSCODE_projectsign = 'WzSYg'



@api_view(['POST'])
def sendEmail(request):
    try:
        destination = request.data.get('destination')
        projectsign = 'evsM7'
        varsdict = {'NameC':'c','NameE':'e'}
        response = xsendEmail(destination,projectsign,varsdict)
        if response.get('status'):
            pass
        else:
            raise InvestError(code=3002,msg=response)
        return JSONResponse(SuccessResponse(response))
    except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
    except Exception:
        catchexcption(request)
        return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

def xsendEmail(destination,projectsign,vars=None):
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
    submail.add_to(destination,)

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
    submail.set_project(projectsign)

    '''
    Optional para
    submail email text content filter
    @Multi-para
    '''
    if vars:
        submail.vars = vars
    # submail.add_var('NameC', 'c')
    # submail.add_var('NameE', 'e')

    '''
    Optional para
    submail email link content filter
    @Multi-para
    '''
    # submail.add_link('developer', 'http://submail.cn/chs/developer')
    # submail.add_link('store', 'http://submail.cn/chs/store')

    '''
    Optional para
    email headers
    @Multi-para
    '''
    submail.add_header('X-Accept', 'zh-cn')
    submail.add_header('X-Mailer', 'leo App')
    response = submail.xsend()
    return response


@api_view(['POST'])
@throttle_classes([AnonRateThrottle])
def sendSmscode(request):
    try :
        destination = request.data.get('destination')
        mobilecode = MobileAuthCode(mobile=destination)
        mobilecode.save()
        varsdict = {'code': mobilecode.code, 'time': '10'}
        response = xsendSms(destination, SMSCODE_projectsign, varsdict)
        success = response.get('status',None)
        if success:
            response['smstoken'] = mobilecode.token
        else:
            raise InvestError(code=30011,msg=response)
        return JSONResponse(SuccessResponse(response))
    except InvestError as err:
        return JSONResponse(InvestErrorResponse(err))
    except Exception:
        catchexcption(request)
        return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

@api_view(['POST'])
def checkSmsCode(request):
    try :
        data = request.data
        mobilecode = data.pop('mobilecode', None)
        mobilecodetoken = data.pop('mobilecodetoken', None)
        mobile = data.pop('mobile',None)
        if mobile and mobilecode and mobilecodetoken:
            try:
                mobileauthcode = MobileAuthCode.objects.get(mobile=mobile, code=mobilecode, token=mobilecodetoken)
            except MobileAuthCode.DoesNotExist:
                raise InvestError(code=2005)
            else:
                if mobileauthcode.isexpired():
                    raise InvestError(code=20051)
        else:
            raise InvestError(code=20072)
        return JSONResponse(SuccessResponse('验证通过'))
    except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
    except Exception:
        catchexcption(request)
        return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))




def xsendSms(destination,projectsign,vars=None):
    submail = MESSAGEXsend(MESSAGE_CONFIGS)

    '''
    Optional para
    recipient cell phone number
    @Multi-para
    '''
    submail.add_to(destination)

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
    submail.set_project(projectsign)

    '''
    Optional para
    submail email text content filter
    @Multi-para
    '''
    if vars:
        submail.vars = vars
    # submail.add_var('code', '198276')

    response = submail.xsend()
    return response


@api_view(['POST'])
def sendInternationalsmscode(request):
    try :
        destination = request.data.get('destination')
        mobilecode = MobileAuthCode(mobile=destination)
        mobilecode.save()
        varsdict = {'code': mobilecode.code, 'time': '10'}
        response = xsendInternationalsms(destination, SMSCODE_projectsign, varsdict)
        success = response.get('status',None)
        if success:
            response['smstoken'] = mobilecode.token
        else:
            raise InvestError(code=30012,msg=response)
        return JSONResponse(SuccessResponse(response))
    except InvestError as err:
        return JSONResponse(InvestErrorResponse(err))
    except Exception:
        catchexcption(request)
        return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))


def xsendInternationalsms(destination, projectsign, vars=None):
    submail = MESSAGEXsend(INTERNATIONALMESSAGE_CONFIGS)

    '''
    Optional para
    recipient cell phone number
    @Multi-para
    '''
    submail.add_to(destination)

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
    submail.set_project(projectsign)

    '''
    Optional para
    submail email text content filter
    @Multi-para
    '''
    if vars:
        submail.vars = vars
    # submail.add_var('code', '198276')

    response = submail.xsend()
    return response
