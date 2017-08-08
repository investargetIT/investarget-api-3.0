# #coding=utf-8
# import json
# import os
# import traceback
# import urllib
# import urllib2
#
# import requests
#
#
#
# def get_access_token(appid,secret,code):
#     try:
#         url = 'https://api.weixin.qq.com/sns/oauth2/access_token?appid=%s&secret=%s&code=%s&grant_type=authorization_code' % (
#         appid, secret, code)
#         response = requests.get(url)
#         response = json.dump(response)
#         access_token = response.get('access_token')
#         openid = response.get('openid')
#         scope = str(response.get('scope')).split(',')   #授权作用域
#         if access_token and openid:
#             if 'snsapi_userinfo' in scope:
#                 try:
#                     user = MyUser.objects.filter(weixinopenid=response.get('unionid'))
#
#                 except MyUser.DoesNotExist:
#                     weixin_info = get_userinfo(access_token,openid)
#                     user = MyUser.objects.create(weixin_info)
#
#                 token_userinfo = maketoken(user, clienttype=4)
#                 resp = {
#                         "success": True,
#                         "user_info": token_userinfo,  # response contain user_info and token
#                     }
#             else:
#                 resp = {
#                     'success':False,
#                     'user_info':None,
#                     'error':'授权空间不包括获取个人信息的权限',
#                 }
#             return JSONResponse(resp)
#     except:
#         response = {
#             'success': False,
#             'error': traceback.format_exc().split('\n')[-2],
#         }
#         return JSONResponse(response)
#
#
#
# def get_userinfo(access_token,openid):
#     url = 'https://api.weixin.qq.com/sns/userinfo?access_token=%s&openid=%s'%(access_token,openid)
#     response = requests.get(url)
#     return response
#
#
# # example:
# # def downloader(request):
# #     url_info , key = downloadheaderimage('http://www.appcoda.com/wp-content/uploads/2015/12/linked-in-sign-in-1024x722.jpg','0001')
# #     return JSONResponse({'url':url_info,'key':key})
#
# def downloadheaderimage(imageurl, imagename):
#     """
#     :param imageurl: 图片外链
#     :param imagename: 图片key
#     下载微信头像，上传至七牛云，返回七牛图片地址及图片key
#     """
#     try:
#         res = requests.get(imageurl)
#         if str(res.status_code) != '200':
#             return None,None
#         else:
#             filename = os.path.join(weixinfilepath, imagename + '.jpg')
#             with open(filename, 'wb') as f:
#                 f.write(res.content)
#     except Exception:
#         return {'error': traceback.format_exc().split('\n')[-2]},None
#
#     filepath = weixinfilepath + '/%s.jpg' % imagename
#     upload_bucket = 'image'
#     success , url_info, key = qiniuuploadfilepath(filepath,upload_bucket)
#     if success:
#         return url_info , key
#     else:
#         return url_info , None