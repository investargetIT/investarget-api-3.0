#coding=utf-8
# Create your views here.
import datetime
import json
import random
import string
import traceback

import qiniu

from qiniu import BucketManager
from qiniu.services.storage.uploader import _Resume, put_file
from rest_framework.decorators import api_view

from third.thirdconfig import qiniu_url, ACCESS_KEY, SECRET_KEY, fops, pipeline
from utils.customClass import JSONResponse, InvestError, MyUploadProgressRecorder
from utils.util import InvestErrorResponse, ExceptionResponse, SuccessResponse

#覆盖上传
@api_view(['POST'])
def qiniu_coverupload(request):
    try:
        bucket_name = request.GET.get('bucket')
        key = request.GET.get('key')
        if not bucket_name or not key or bucket_name not in qiniu_url.keys():
            raise InvestError(2020,msg='bucket/key error')
        data_dict = request.FILES
        uploaddata = None
        for keya in data_dict.keys():
            uploaddata = data_dict[keya]
        q = qiniu.Auth(ACCESS_KEY, SECRET_KEY)
        filetype = str(uploaddata.name).split('.')[-1]
        if filetype != 'pdf' and bucket_name not in ['image', u'image']:
            saveas_key = qiniu.urlsafe_base64_encode('file:%s' % (key.split('.')[0] + '.pdf'))
            persistentOps = fops + '|saveas/' + saveas_key
            policy = {
                'persistentOps': persistentOps,
                # 'persistentPipeline': pipeline,
                'deleteAfterDays': 1,
            }
        else:
            policy = None
        print key
        params = {'x:a':'a'}
        mime_type = uploaddata.content_type
        token = q.upload_token(bucket_name, key, 3600,policy=policy)
        progress_handler = lambda progress,total:progress / total
        uploader = _Resume(token,key,uploaddata,uploaddata.size,params,mime_type,progress_handler,upload_progress_recorder=MyUploadProgressRecorder(),modify_time=None,file_name=key)
        ret,info = uploader.upload()
        if info is not None:
            if info.status_code == 200:
                return_url = getUrlWithBucketAndKey(bucket_name,ret['key'])
            else:
                raise InvestError(2020,msg=str(info))
        else:
            raise InvestError(2020,msg=str(ret))
        if policy:
            key = key.split('.')[0] + '.pdf'
        return JSONResponse(SuccessResponse({'key':key,'url':return_url}))
    except InvestError as err:
        return JSONResponse(InvestErrorResponse(err))
    except Exception:
        return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))


@api_view(['POST'])
def bigfileupload(request):
    """
    分片上传
    """
    try:
        bucket_name = request.GET.get('bucket')
        if bucket_name not in qiniu_url.keys():
            raise InvestError(2020,msg='bucket error')
        data_dict = request.FILES
        uploaddata = None
        for key in data_dict.keys():
            uploaddata = data_dict[key]
        q = qiniu.Auth(ACCESS_KEY, SECRET_KEY)
        filetype = str(uploaddata.name).split('.')[-1]
        key = datetime.datetime.now().strftime('%Y%m%d%H%M%s') + ''.join(random.sample(string.ascii_lowercase,6)) + '.' + filetype
        if filetype != 'pdf' and bucket_name not in ['image', u'image']:
            saveas_key = qiniu.urlsafe_base64_encode('file:%s' % (key.split('.')[0] + '.pdf'))
            persistentOps = fops + '|saveas/' + saveas_key
            policy = {
                'persistentOps': persistentOps,
                # 'persistentPipeline': pipeline,
                'deleteAfterDays': 1,
            }
        else:
            policy = None
        print key
        params = {'x:a':'a'}
        mime_type = uploaddata.content_type
        token = q.upload_token(bucket_name, key, 3600,policy=policy)
        progress_handler = lambda progress,total:progress / total
        uploader = _Resume(token,key,uploaddata,uploaddata.size,params,mime_type,progress_handler,upload_progress_recorder=MyUploadProgressRecorder(),modify_time=None,file_name=key)
        ret,info = uploader.upload()
        if info is not None:
            if info.status_code == 200:
                return_url = getUrlWithBucketAndKey(bucket_name,ret['key'])
            else:
                raise InvestError(2020,msg=str(info))
        else:
            raise InvestError(2020,msg=str(ret))
        if policy:
            key = key.split('.')[0] + '.pdf'
        return JSONResponse(SuccessResponse({'key':key,'url':return_url}))
    except InvestError as err:
        return JSONResponse(InvestErrorResponse(err))
    except Exception:
        return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

@api_view(['POST'])
def qiniu_uploadtoken(request):
    try:
        data = request.data
        bucket_name = data['bucket']
        key = data['key']
        if not bucket_name or not key:
            raise InvestError(2020,msg='bucket/key error')
        policy = data.get('policy',None)
        q = qiniu.Auth(ACCESS_KEY, SECRET_KEY)
        token = q.upload_token(bucket_name, key, 3600, policy=policy)
        return JSONResponse(SuccessResponse(token))
    except InvestError as err:
        return JSONResponse(InvestErrorResponse(err))
    except Exception:
        return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

@api_view(['POST'])
def qiniu_downloadurl(request):
    try:
        data = request.data
        bucket_name = data['bucket']
        key = data['key']
        return_url = getUrlWithBucketAndKey(bucket_name,key)
        return JSONResponse(SuccessResponse(return_url))
    except InvestError as err:
        return JSONResponse(InvestErrorResponse(err))
    except Exception:
        return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))


@api_view(['POST'])
def qiniu_deletefile(request):
    """
    param：{'bucket':str,'key':str}
    """
    try:
        data = request.data
        bucket = data.get('bucket',None)
        key = data.get('key',None)
        if bucket not in qiniu_url.keys():
            return None
        ret, info = deleteqiniufile(bucket,key)
        if info.req_id is None or info.status_code != 200:
            raise InvestError(7010,msg=json.dumps(info.text_body))
        return JSONResponse(SuccessResponse('删除成功'))
    except InvestError as err:
        return JSONResponse(InvestErrorResponse(err))
    except Exception:
        return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

def deleteqiniufile(bucket,key):
    q = qiniu.Auth(ACCESS_KEY, SECRET_KEY)
    bucketManager = BucketManager(q)
    ret, info = bucketManager.delete(bucket, key)
    return ret, info

def getUrlWithBucketAndKey(bucket,key):
    if bucket not in qiniu_url.keys():
        return None
    q = qiniu.Auth(ACCESS_KEY, SECRET_KEY)
    return_url = "https://%s/%s" % (qiniu_url[bucket], key)
    if bucket == 'file':
        return_url = q.private_download_url(return_url)
    return return_url

#上传本地文件
def qiniuuploadfile(filepath, bucket_name):
    q = qiniu.Auth(ACCESS_KEY, SECRET_KEY)
    filetype = filepath.split('.')[-1]
    key = "%s.%s" % (datetime.datetime.now().strftime('%Y%m%d%H%M%s')+''.join(random.sample(string.ascii_lowercase,5)), filetype)   # key 文件名
    print key
    token = q.upload_token(bucket_name, key, 3600, policy={}, strict_policy=True)
    ret, info = put_file(token, key, filepath)
    if info is not None:
        if info.status_code == 200:
            return True, "http://%s/%s" % (qiniu_url['file'], ret["key"]),key
        else:
            return False, str(info),None
    else:
        return False,None,None
