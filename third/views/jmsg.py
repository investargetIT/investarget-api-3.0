#coding=utf-8
import json
import time
import traceback
import base64
import datetime
from jmessage import common, requests
from rest_framework.decorators import api_view

from third.thirdconfig import my_product
from utils.customClass import JSONResponse, InvestError
from utils.util import msdstring, SuccessResponse, InvestErrorResponse, ExceptionResponse, checkRequestToken, \
    logexcption
import random, string

app_key = my_product['app_key']
master_secret = my_product['master_secret']
jmessage = common.JMessage(app_key, master_secret)


def regist(username, password, nickname=None):
    users = jmessage.create_users()
    user = [users.build_user(username=username, password=password, nickname=nickname)]
    response = users.regist_user(user)
    return json.loads(response.content)


def makeauth_payload():
    random_str = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(32))
    timestamp = int(round(time.time() * 1000))    #13位时间戳
    signature = "appkey=%s&timestamp=%s&random_str=%s&key=%s"%(app_key, timestamp, random_str, master_secret)
    signature = msdstring(signature)
    return {
        'appkey':app_key,
        'random_str':random_str,
        'signature':signature,
        'timestamp':timestamp,
    }


@api_view(['GET'])
@checkRequestToken()
def getauth(request):
    try:
        auth = makeauth_payload()
        return JSONResponse(SuccessResponse(auth))
    except InvestError as err:
        return JSONResponse(InvestErrorResponse(err))
    except Exception:
        return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))


report_url = 'https://report.im.jpush.cn/v2'


def http_result(r):
    if r.status_code == requests.codes.ok:
        return True, r.json()
    else:
        return False, r.text


def test(request):
    downloadChatHistoryMessages()
    return JSONResponse(SuccessResponse({'ss':'ss'}))


def downloadChatHistoryMessages():
    begin_time = (datetime.datetime.now() - datetime.timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
    end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    url = report_url + '/messages?count=1000&begin_time=%s&end_time=%s' % (begin_time, end_time)
    downloadChatMessagesWithUrl(url)


def downloadChatMessagesWithUrl(url):
    headers = {}
    headers['connection'] = 'keep-alive'
    headers['content-type'] = 'application/json;charset:utf-8'
    headers['Authorization'] = 'Basic ' + base64.b64encode('%s:%s' % (app_key, master_secret))
    success, res = http_result(requests.get(url, headers=headers))
    if success:
        messages = res.get('messages', [])
        saveMessages(messages)
        if res.get('cursor'):
            url = report_url + '/messages?cursor=%s'%res.get('cursor')
            downloadChatMessagesWithUrl(url)
    else:
        logexcption(msg=str({'downloadchatmsg':res}))


def saveMessages(messages):
    for message in messages:
        if isinstance(message, dict) and message.get('msgid', None) is not None:

            print(message)


# u'sui_mtime': 1521514266,
# u'version': 1,
# u'msg_type': u'text',
# u'msgid': 737628715,
# u'from_platform': u'api',
# u'target_id': u'123456789',
# u'target_type': u'single',
# u'from_type': u'admin',
# u'msg_ctime': 1521514290823,
# u'msg_level': 0,
# u'msg_body': {
# 	u'text': u'测试测试',
# 	u'extras': {}
# },
# u'create_time': 1521514290,
# u'from_appkey': u'aeaa17fd17c401b0d0742423',
# u'from_id': u'123456'