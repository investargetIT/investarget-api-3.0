#coding:utf-8
import json
import ssl
import traceback

import datetime
import urllib2
import requests

# Create your views here.
from rest_framework import viewsets
from rest_framework.decorators import api_view

from mongoDoc.models import WXContentData
from mongoDoc.serializers import WXContentDataSerializer
from utils.customClass import JSONResponse, InvestError
from utils.util import SuccessResponse, InvestErrorResponse, ExceptionResponse, catchexcption
APPID = '9845160'
APIKEY = 'xxnuhuvogLrRR7jCH9vKh2Tt'
APISECRET = 'pmnYqjuzEXpnzi96FbNlm4PxvWUw460y'

class WXView(viewsets.ModelViewSet):

    queryset = WXContentData.objects.all()
    serializer_class = WXContentDataSerializer
    def list(self, request, *args, **kwargs):
        try:
            count = self.queryset.count()
            serializer = WXContentDataSerializer(self.queryset,many=True)
            return JSONResponse(SuccessResponse({'count':count,'data':serializer.data}))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            serializer = WXContentDataSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
            return JSONResponse(SuccessResponse(serializer.data))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))
from aip import AipNlp
aipNlp = AipNlp(APPID, APIKEY, APISECRET)

@api_view(['GET'])
def getBaiDuNLP_Accesstoken(request):
    text = '请问是否有关于北京市四合院销售市场分析，谢谢！[抱拳]'
    # result = aipNlp.depParser(text, {'mode': 0})
    # print 'depParser mode 0'
    # print result
    # result = aipNlp.depParser(text, {'mode': 1})
    # print '******\n'
    # print 'depParser mode 1'
    # print result
    # print '******'+'\n'+'lexer'
    result = aipNlp.lexer(text)
    print result

    return JSONResponse({'ss':'ss'})
