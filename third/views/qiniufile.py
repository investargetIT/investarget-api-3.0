#coding=utf-8


# Create your views here.
import datetime
import qiniu
import time

from qiniu import put_data
from qiniu.services.storage.uploader import _Resume, put_file
from rest_framework.decorators import api_view

from utils.customClass import JSONResponse

ACCESS_KEY = 'NJkzgfMrIi-wL_gJyeLfU4dSqXyk5eeGrI7COPPu'
SECRET_KEY = '6hWJqsm9xdAcGFPyr-MHwVKpdrQ25eJbf2JsaQ8U'
qiniu_url = 'o79atf82v.qnssl.com'
policy={
 'callbackUrl':'http://your.domain.com/callback.php',
 'callbackBody':'filename=$(fname)&filesize=$(fsize)'
 }

def qiniuupload(request):
    bucket_name = request.GET.get('bucket')
    data_dict = request.FILES
    uploaddata = None
    for key in data_dict.keys():
        uploaddata = data_dict[key]
    q = qiniu.Auth(ACCESS_KEY, SECRET_KEY)
    filetype = str(uploaddata.name).split('.')[-1]
    key = "%s.%s" % (str(time.time()), filetype)   #key 文件名
    token = q.upload_token(bucket_name, key, 3600)
    ret, info = put_data(token, key, uploaddata)
    return_url,error = None,None
    if info is not None:
        if info.status_code == 200:
            return_url = "http://%s/%s" % (qiniu_url, ret["key"])
        else:
            error = str(info)
    return JSONResponse({'key':key,'url':return_url,'error':error})


def qiniuuploadfilepath(filepath,bucket_name):
    q = qiniu.Auth(ACCESS_KEY, SECRET_KEY)
    filetype = filepath.split('.')[-1]
    key = "%s.%s" % (str(time.time()), filetype)   #key 文件名
    print key
    token = q.upload_token(bucket_name, key, 3600,policy={},strict_policy=True)
    ret, info = put_file(token, key, filepath)
    if info is not None:
        if info.status_code == 200:
            return True, "http://%s/%s" % (qiniu_url, ret["key"]),key
        else:
            return False, str(info),None
    else:
        return False,None,None





@api_view(['POST'])
def bigfileupload(request):
    bucket_name = request.GET.get('bucket')
    data_dict = request.FILES
    uploaddata = None
    for key in data_dict.keys():
        uploaddata = data_dict[key]
    q = qiniu.Auth(ACCESS_KEY, SECRET_KEY)
    # filetype = str(uploaddata.name).split('.')[-1]
    # key = "%s.%s" % (str(time.time()), filetype)  # key 文件名
    key = uploaddata.name
    print key
    params = {'x:a':'a'}
    mime_type = uploaddata.content_type
    token = q.upload_token(bucket_name, key, 3600)
    progress_handler = lambda progress , total:progress

    # ret, info = put_data(token,key,uploaddata,params,mime_type,progress_handler=progress_handler)
    uploader = _Resume(token,key,uploaddata,uploaddata.size,params,mime_type,progress_handler,upload_progress_recorder=None,modify_time=None,file_name=key)
    return_url, error = None, None
    ret,info = uploader.upload()
    print ret,info
    if info is not None:
        if info.status_code == 200:
            return_url = "http://%s/%s" % (qiniu_url, ret["key"])
        else:
            error = str(info)
    return JSONResponse({'key': key, 'url': return_url, 'error': error})
