#coding=utf-8
import json
import traceback

import requests

from MyUserSys.models import MyUser, MyToken
from MyUserSys.myauth import JSONResponse
from MyUserSys.views import maketoken





def get_access_token(client_id,client_secret,code):
    try:
        url = 'https://www.linkedin.com/oauth/v2/accessToken'
        params = {
            'grant_type':'authorization_code',
            'code':code,
            'redirect_uri': '',
            'client_id': client_id,
            'client_secret': client_secret,
        }
        headers = {
            'Content-Type':'application/x-www-form-urlencoded;'
        }
        response = requests.get(url=url,params=params,headers=headers)
        response = json.dump(response)
        access_token = response.get('access_token')
        expires_in = response.get('expires_in')
        if access_token and expires_in:
            try:
                user = MyUser.objects.filter(weixinopenid=response.get('unionid'))

            except MyUser.DoesNotExist:
                weixin_info = get_userinfo(access_token)
                user = MyUser.objects.create(weixin_info)

            token_userinfo = maketoken(user, clienttype=4)
            resp = {
                "success": True,
                "user_info": token_userinfo,  # response contain user_info and token
            }
            return JSONResponse(resp)
    except:
        response = {
            'success': False,
            'error': traceback.format_exc().split('\n')[-2],
        }
        return JSONResponse(response)


def get_userinfo(access_token):
    url = 'https://api.linkedin.com/v1/people/~?format=json'
    headers = {}
    headers['Authorization'] = 'Bearer ' + access_token
    response = requests.get(url=url,headers=headers)
    return response
