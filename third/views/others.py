#coding=utf-8
import json
import os
import traceback

import requests
from django.http import StreamingHttpResponse
from rest_framework.decorators import api_view

from invest.settings import APILOG_PATH
from utils.customClass import JSONResponse, InvestError
from utils.util import SuccessResponse, catchexcption, ExceptionResponse, InvestErrorResponse, checkrequesttoken


@api_view(['GET'])
def getcurrencyreat(request):
    try:
        tokenkey = request.META.get('HTTP_TOKEN')
        checkrequesttoken(tokenkey)
        tcur = request.GET.get('tcur', None)
        scur = request.GET.get('scur', None)
        if not tcur or not scur:
            raise InvestError(20072)
        response = requests.get('https://sapi.k780.com/?app=finance.rate&scur=%s&tcur=%s&appkey=18220&sign=9b97118c7cf61df11c736c79ce94dcf9'% (scur, tcur)).content
        response = json.loads(response)
        if isinstance(response,dict):
            success = response.get('success',False)
            if success in ['1',True]:
                result = response.get('result',{})
            else:
                raise InvestError(code=2007,msg=response.get('msg',None))
        else:
            raise InvestError(code=2007,msg=response)
        return JSONResponse(SuccessResponse(result))
    except InvestError as err:
        return JSONResponse(InvestErrorResponse(err))
    except Exception:
        catchexcption(request)
        return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))


@api_view(['POST'])
def ccupload(request):
    try:
        data_dict = request.FILES
        uploaddata = None
        for keya in data_dict.keys():
            uploaddata = data_dict[keya]
        urlstr = 'http://bcr2.intsig.net/BCRService/BCR_VCF2?user=summer.xia@investarget.com&pass=P8YSCG7AQLM66S7M&json=1&lang=15'
        response = requests.post(urlstr,uploaddata)
        return JSONResponse(SuccessResponse(response.content))
    except InvestError as err:
        return JSONResponse(InvestErrorResponse(err))
    except Exception:
        return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

import qrcode

def makeQRCode(content,path):
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(content)
    qr.make(fit=True)
    img = qr.make_image()
    img.save(path)

@api_view(['GET'])
def getQRCode(request):
    """
    获取二维码
    """
    try:
        request.user = checkrequesttoken(request.GET.get('acw_tk'))
        url = request.GET.get('url',None)
        if url:
            qrcode_path = APILOG_PATH['qrcode']
            def file_iterator(fn, chunk_size=512):
                while True:
                    c = fn.read(chunk_size)
                    if c:
                        yield c
                    else:
                        break
            makeQRCode(url,qrcode_path)
            fn = open(qrcode_path, 'rb')
            response = StreamingHttpResponse(file_iterator(fn))
            response['Content-Type'] = 'application/octet-stream'
            response["content-disposition"] = 'attachment;filename=qrcode.png'
            os.remove(qrcode_path)
        else:
            raise InvestError(50010, msg='二维码生成失败')
        return response
    except InvestError as err:
        return JSONResponse(InvestErrorResponse(err))
    except Exception:
        return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))