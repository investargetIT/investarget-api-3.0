#coding=utf-8
import json
import traceback

import datetime

from SUBMAIL_PYTHON_SDK_MAIL_AND_MESSAGE_WITH_ADDRESSBOOK.mail_xsend import MAILXsend
from SUBMAIL_PYTHON_SDK_MAIL_AND_MESSAGE_WITH_ADDRESSBOOK.message_xsend import MESSAGEXsend
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from third.models import MobileAuthCode
from utils.customClass import JSONResponse, InvestError
from utils.util import SuccessResponse, catchexcption, ExceptionResponse, InvestErrorResponse, checkIPAddress




'''
（海拓）注册短信验证码模板
'''
SMSCODE_projectsign = {'1':'WzSYg','2':'tybmL4'}


MAIL_CONFIGS = {}
'''
Mail appid
'''
MAIL_CONFIGS['appid'] = '11182'

'''
Mail appkey
'''
MAIL_CONFIGS['appkey'] = '06c390e5c2488a2c1e06080f86987f53'

'''
Mail Sign type
md5/sha1/normal
'''
MAIL_CONFIGS['sign_type'] = 'md5'

'''
Message configs start
message_configs['appid']
message_configs['appkey']
message_configs['sign_type']
'''
MESSAGE_CONFIGS = {}
'''
Message appid
'''
MESSAGE_CONFIGS['appid'] = '13952'

'''
Message appkey
'''
MESSAGE_CONFIGS['appkey'] = '22a2a05b1a95d9c86079b3ba439466de'

'''
Message Sign type
md5/sha1/normal
'''
MESSAGE_CONFIGS['sign_type'] = 'md5'

'''
Message configs end
'''



INTERNATIONALMESSAGE_CONFIGS = {}
'''
InternationalMessage appid
'''
INTERNATIONALMESSAGE_CONFIGS['appid'] = '60060'

'''
InternationalMessage appkey
'''
INTERNATIONALMESSAGE_CONFIGS['appkey'] = '347c8b402222ae2643957c1f5d288058'

'''
InternationalMessage Sign type
md5/sha1/normal
'''
INTERNATIONALMESSAGE_CONFIGS['sign_type'] = 'md5'

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
        source = request.META['HTTP_SOURCE']
        if request.META.has_key('HTTP_X_FORWARDED_FOR'):
            ip = request.META['HTTP_X_FORWARDED_FOR']
        else:
            ip = request.META['REMOTE_ADDR']
        if ip:
            times = checkIPAddress(ip)
            if times > 100:
                raise InvestError(code=3004,msg='单位时间内只能获取三次验证码')
        else:
            raise InvestError(code=3003)
        destination = request.data.get('mobile')
        areacode = request.data.get('areacode')
        now = datetime.datetime.now()
        start = now - datetime.timedelta(minutes=1)
        if MobileAuthCode.objects.filter(createTime__gt=start).filter(mobile=destination,is_deleted=False).exists():
            raise InvestError(code=3004)
        mobilecode = MobileAuthCode(mobile=destination)
        mobilecode.save()
        varsdict = {'code': mobilecode.code, 'time': '30'}
        if areacode in ['86',86]:
            response = xsendSms(destination, SMSCODE_projectsign[str(source)], varsdict)
        else:
            response = xsendInternationalsms('+%s'%areacode + destination, SMSCODE_projectsign[str(source)], varsdict)
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

    return submail.xsend()




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



# if request.META.has_key('HTTP_X_FORWARDED_FOR'):
#     ip =  request.META['HTTP_X_FORWARDED_FOR']
# else:
#     ip = request.META['REMOTE_ADDR']