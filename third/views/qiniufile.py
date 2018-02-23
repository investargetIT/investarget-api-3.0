#coding=utf-8
# Create your views here.
import datetime
import json
import os
import random
import string
import subprocess
import threading
import traceback

import qiniu
import requests
from django.http import StreamingHttpResponse

from qiniu import BucketManager
from qiniu.services.storage.uploader import _Resume, put_file
from rest_framework.decorators import api_view

from invest.settings import APILOG_PATH
from third.thirdconfig import qiniu_url, ACCESS_KEY, SECRET_KEY, fops, pipeline
from utils.customClass import JSONResponse, InvestError, MyUploadProgressRecorder
from utils.somedef import addWaterMark, file_iterator
from utils.util import InvestErrorResponse, ExceptionResponse, SuccessResponse, loginTokenIsAvailable, checkrequesttoken, \
    catchexcption, checkRequestToken, logexcption


#覆盖上传
@api_view(['POST'])
def qiniu_coverupload(request):
    try:
        isChangeToPdf = request.GET.get('topdf', True)
        bucket_name = request.GET.get('bucket')
        key = request.GET.get('key')
        if not bucket_name or not key or bucket_name not in qiniu_url.keys():
            raise InvestError(2020,msg='bucket/key error')
        deleteqiniufile(bucket_name, key)
        data_dict = request.FILES
        uploaddata = None
        for key in data_dict.keys():
            uploaddata = data_dict[key]
        q = qiniu.Auth(ACCESS_KEY, SECRET_KEY)
        filetype = str(uploaddata.name).split('.')[-1]
        randomPrefix = datetime.datetime.now().strftime('%Y%m%d%H%M%s') + ''.join(random.sample(string.ascii_lowercase, 6))
        inputFileKey = randomPrefix + '.' + filetype
        outputFileKey = randomPrefix + '.' + 'pdf'
        if filetype in ['xlsx', 'doc', 'docx', 'xls', 'ppt', 'pptx'] and isChangeToPdf in ['true', True, '1', 1, u'true']:
            isChange = True
            dirpath = APILOG_PATH['uploadFilePath']
            if not os.path.exists(dirpath):
                os.makedirs(dirpath)
            inputFilePath = os.path.join(dirpath, inputFileKey)
            outputFilePath = os.path.join(dirpath, outputFileKey)
            with open(inputFilePath, 'wb+') as destination:
                for chunk in uploaddata.chunks():
                    destination.write(chunk)
            convertAndUploadOffice(inputFilePath, outputFilePath, bucket_name, outputFileKey)
        else:
            isChange = False
        params = {'x:a': 'a'}
        mime_type = uploaddata.content_type
        token = q.upload_token(bucket_name, inputFileKey, 3600)
        progress_handler = lambda progress, total: progress / total
        uploader = _Resume(token, inputFileKey, uploaddata, uploaddata.size, params, mime_type, progress_handler,
                           upload_progress_recorder=MyUploadProgressRecorder(), modify_time=None, file_name=uploaddata.name)
        ret, info = uploader.upload()
        if info is not None:
            if info.status_code == 200:
                return_url = getUrlWithBucketAndKey(bucket_name, ret['key'])
            else:
                raise InvestError(2020, msg=str(info))
        else:
            raise InvestError(2020, msg=str(ret))
        if isChange:
            key = outputFileKey
        else:
            key = inputFileKey
        return JSONResponse(SuccessResponse({'key': key, 'url': return_url, 'realfilekey': inputFileKey}))
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
        isChangeToPdf = request.GET.get('topdf', True)
        bucket_name = request.GET.get('bucket')
        if bucket_name not in qiniu_url.keys():
            raise InvestError(2020,msg='bucket error')
        data_dict = request.FILES
        uploaddata = None
        for key in data_dict.keys():
            uploaddata = data_dict[key]
        q = qiniu.Auth(ACCESS_KEY, SECRET_KEY)
        filetype = str(uploaddata.name).split('.')[-1]
        randomPrefix = datetime.datetime.now().strftime('%Y%m%d%H%M%s') + ''.join(
            random.sample(string.ascii_lowercase, 6))
        inputFileKey = randomPrefix + '.' + filetype
        outputFileKey = randomPrefix + '.' + 'pdf'
        if filetype in ['xlsx', 'doc', 'docx', 'xls', 'ppt', 'pptx'] and isChangeToPdf in ['true', True, '1', 1,
                                                                                           u'true']:
            isChange = True
            dirpath = APILOG_PATH['uploadFilePath']
            if not os.path.exists(dirpath):
                os.makedirs(dirpath)
            inputFilePath = os.path.join(dirpath, inputFileKey)
            outputFilePath = os.path.join(dirpath, outputFileKey)
            with open(inputFilePath, 'wb+') as destination:
                for chunk in uploaddata.chunks():
                    destination.write(chunk)
            convertAndUploadOffice(inputFilePath, outputFilePath, bucket_name, outputFileKey)
        else:
            isChange = False
        params = {'x:a': 'a'}
        mime_type = uploaddata.content_type
        token = q.upload_token(bucket_name, inputFileKey, 3600)
        progress_handler = lambda progress, total: progress / total
        uploader = _Resume(token, inputFileKey, uploaddata, uploaddata.size, params, mime_type, progress_handler,
                           upload_progress_recorder=MyUploadProgressRecorder(), modify_time=None, file_name=uploaddata.name)
        ret, info = uploader.upload()
        if info is not None:
            if info.status_code == 200:
                return_url = getUrlWithBucketAndKey(bucket_name, ret['key'])
            else:
                raise InvestError(2020, msg=str(info))
        else:
            raise InvestError(2020, msg=str(ret))
        if isChange:
            key = outputFileKey
        else:
            key = inputFileKey
        return JSONResponse(SuccessResponse({'key':key,'url':return_url,'realfilekey':inputFileKey}))
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
    if bucket and key:
        ret, info = bucketManager.delete(bucket, key)
        return ret, info

def getUrlWithBucketAndKey(bucket,key):
    if bucket not in qiniu_url.keys():
        return None
    if key is None:
        return None
    q = qiniu.Auth(ACCESS_KEY, SECRET_KEY)
    return_url = "https://%s/%s" % (qiniu_url[bucket], key)
    if bucket == 'file':
        return_url = q.private_download_url(return_url)
    return return_url

#上传本地文件
def qiniuuploadfile(filepath, bucket_name, bucket_key):
    q = qiniu.Auth(ACCESS_KEY, SECRET_KEY)
    token = q.upload_token(bucket_name, bucket_key, 3600, policy={}, strict_policy=True)
    ret, info = put_file(token, bucket_key, filepath)
    if info is not None:
        if info.status_code == 200:
            return True, getUrlWithBucketAndKey(bucket_name, ret["key"]),bucket_key
        else:
            return False, str(info),None
    else:
        return False,None,None

#下载文件到本地
def downloadFileToPath(key,bucket,path):
    try:
        download_url = getUrlWithBucketAndKey(bucket, key)
        if download_url is None:
            raise InvestError(8002, msg='bucket/key error')
        r = requests.get(download_url)
        if r.status_code != 200:
            raise InvestError(8002, msg=repr(r.content))
        with open(path, "wb") as code:
            code.write(r.content)
    except Exception:
        return None
    else:
        return path


@api_view(['GET'])
def testconvert(request):
    try:
        convertAndUploadOffice('aaa','aaa','aaa','aaaa')
        import time
        time.sleep(5)
        return JSONResponse(SuccessResponse({}))
    except InvestError as err:
        return JSONResponse(InvestErrorResponse(err))
    except Exception:
        catchexcption(request)
        return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))



def convertAndUploadOffice(inputpath, outputpath, bucket_name, bucket_key):
    """
    :param inputpath: 源文件路径
    :param outputpath: 转化后文件路径
    :return:
    """
    class convertAndUploadOfficeThread(threading.Thread):
        def run(self):
            try:
                import sys
                commandstr = 'python /opt/openoffice4/program/officeConvert.py %s %s &' % (inputpath, outputpath)
                import subprocess
                returnCode = subprocess.call(commandstr,shell=True) #阻塞运行
                print returnCode
            except ImportError:
                logexcption(msg='引入模块失败')
            except Exception:
                logexcption(msg='文件转换失败')
            if os.path.exists(outputpath):
                success, url, key = qiniuuploadfile(outputpath, bucket_name, bucket_key)
            # if os.path.exists(inputpath):
            #     os.remove(inputpath)
            # if os.path.exists(outputpath):
            #     os.remove(outputpath)
    convertAndUploadOfficeThread().start()