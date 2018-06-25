#coding=utf-8
import json
import traceback
import requests

from third.thirdconfig import WX_APPID, WX_APPSECRET
from utils.customClass import InvestError



def get_openid(code):
    try:
        if code:
            url = 'https://api.weixin.qq.com/sns/jscode2session?appid=%s&secret=%s&js_code=%s&grant_type=authorization_code' % (WX_APPID, WX_APPSECRET, code)
            response = requests.get(url).content
            res = json.loads(response)
            openid = res.get('openid')
            if openid:
                return openid
    except Exception:
        raise InvestError(2007, msg='获取openid失败')
    else:
        return None

