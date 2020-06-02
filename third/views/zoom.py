#coding=utf-8
import base64
import json
import traceback
import requests
from rest_framework.decorators import api_view
from third.thirdconfig import zoom_clientSecrect, zoom_clientId, zoom_redirect_uri
from utils.customClass import JSONResponse, InvestError
from utils.util import catchexcption, ExceptionResponse, SuccessResponse, InvestErrorResponse, read_from_cache, write_to_cache


# 获取请求码
def requestOAuthCode():
    authorize_url = 'https://zoom.us/oauth/authorize'
    params = {'response_type': 'code', 'redirect_uri': zoom_redirect_uri, 'client_id': zoom_clientId}
    requests.get(authorize_url, params=params)


# zoom请求码重定向uri
@api_view(['GET'])
def requestOAuthCodeRedirectURI(request):
    """
    zoom请求码重定向uri
    """
    try:
        code = request.GET.get('code', None)
        token_url = 'https://zoom.us/oauth/token'
        data = {'grant_type': 'authorization_code', 'redirect_uri': zoom_redirect_uri, 'code': code}
        basic = '{0}:{1}'.format(zoom_clientId, zoom_clientSecrect)
        headers = {'Authorization': 'Basic {}'.format(base64.b64encode(basic))}
        response = requests.post(token_url, data=data, headers=headers)
        if response.status_code == 200:
            response = response.json()
            access_token = response['access_token']
            write_to_cache('zoom_access_token', access_token, 3600)
        return JSONResponse(SuccessResponse(response.json()))
    except InvestError as err:
        return JSONResponse(InvestErrorResponse(err))
    except Exception:
        catchexcption(request)
        return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))


## zoom刷新token
# def refreshAccessToken(access_token):
#     token_url = 'https://zoom.us/oauth/token'
#     data = {'grant_type': 'refresh_token', 'refresh_token': access_token}
#     basic = '{0}:{1}'.format(zoom_clientId, zoom_clientSecrect).encode("utf-8")
#     headers = {'Authorization': 'Basic {}'.format(base64.b64encode(basic))}
#     response = requests.post(token_url, data=data, headers=headers)
#     response = json.loads(response)
#     access_token = response['access_token']
#     write_to_cache('zoom_access_token', access_token, 3600)


# 确认是否存在zoom鉴权令牌
@api_view(['GET'])
def accessTokenExists(request):
    """
    确认是否存在zoom鉴权令牌
    """
    try:
        access_token = read_from_cache('zoom_access_token')
        if access_token:
            return JSONResponse(SuccessResponse(True))
        return JSONResponse(SuccessResponse(False))
    except InvestError as err:
        return JSONResponse(InvestErrorResponse(err))
    except Exception:
        catchexcption(request)
        return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))


# zoom获取user会议列表
@api_view(['GET'])
def getUserMesstings(request):
    """
    zoom获取user会议列表
    """
    try:
        access_token = read_from_cache('zoom_access_token')
        if not access_token:
            requestOAuthCode()
            raise InvestError(9100, msg='zoom Access_token无效或不存在, 正在获取，请重新请求')
        else:
            userId = request.GET.get('user')
            meetings_type = request.GET.get('type', 'scheduled')
            page_size = request.GET.get('page_size', 30)
            page_index = request.GET.get('page_index', 1)
            meetings_url = 'https://api.zoom.us/v2/users/{}/meetings'.format(userId)
            params = {'type': meetings_type, 'page_size': page_size, 'page_number': page_index}
            response = requests.get(meetings_url, params=params, headers={'Authorization': 'Bearer  {}'.format(access_token)})
            if response.status_code != 200:
                raise InvestError(2007, msg=response.json()['reason'])
            return JSONResponse(SuccessResponse(response.json()))
    except InvestError as err:
        return JSONResponse(InvestErrorResponse(err))
    except Exception:
        catchexcption(request)
        return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))