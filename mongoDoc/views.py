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

from mongoDoc.models import GroupEmailData, IMChatMessages
from mongoDoc.serializers import GroupEmailDataSerializer, IMChatMessagesSerializer
from utils.customClass import JSONResponse, InvestError
from utils.util import SuccessResponse, InvestErrorResponse, ExceptionResponse, catchexcption, logexcption

APPID = '9845160'
APIKEY = 'xxnuhuvogLrRR7jCH9vKh2Tt'
APISECRET = 'pmnYqjuzEXpnzi96FbNlm4PxvWUw460y'





class GroupEmailDataView(viewsets.ModelViewSet):
    queryset = GroupEmailData.objects.all()
    serializer_class = GroupEmailDataSerializer
    def list(self, request, *args, **kwargs):
        try:
            projtitle = request.GET.get('title')
            queryset = self.queryset
            if projtitle:
                queryset = queryset(projtitle__icontains=projtitle)
            # queryset =queryset(proj__id=13)
            count = queryset.count()
            serializer = GroupEmailDataSerializer(queryset,many=True)
            return JSONResponse(SuccessResponse({'count':count,'data':serializer.data}))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))


def saveSendEmailDataToMongo(data):
    serializer = GroupEmailDataSerializer(data=data)
    try:
        if serializer.is_valid():
            serializer.save()
        else:
            print serializer.error_messages
            raise InvestError(2001,msg=serializer.error_messages)
    except Exception:
        logexcption()

def readSendEmailDataFromMongo():
    start = datetime.datetime.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
    qs = GroupEmailData.objects.filter(savetime__gt=start)
    return GroupEmailDataSerializer(qs,many=True).data

#
# from aip import AipNlp
# aipNlp = AipNlp(APPID, APIKEY, APISECRET)
#
# @api_view(['GET'])
# def getBaiDuNLP_Accesstoken(request):
#     text = '项目地区: 德国，欧洲 项目行业: 消费品 项目类型: 兼并收购 拟交易规模：$ 393,781,776 营业收入（2016）:  $ 273,583,923 EBITDA（2016）：$ 32,830,070'
#     # result = aipNlp.depParser(text, {'mode': 0})
#     # print 'depParser mode 0'
#     # print result
#     # result = aipNlp.depParser(text, {'mode': 1})
#     # print '******\n'
#     # print 'depParser mode 1'
#     # print result
#     # print '******'+'\n'+'lexer'
#     result = aipNlp.lexer(text)
#     print result
#
#     return JSONResponse({'ss':'ss'})


class IMChatMessagesView(viewsets.ModelViewSet):
    queryset = IMChatMessages.objects.all()
    serializer_class = IMChatMessagesSerializer

    def list(self, request, *args, **kwargs):
        try:
            # projtitle = request.GET.get('title')
            queryset = self.queryset
            # if projtitle:
            #     queryset = queryset(projtitle__icontains=projtitle)
            # queryset =queryset(proj__id=13)
            count = queryset.count()
            serializer = self.serializer_class(queryset,many=True)
            return JSONResponse(SuccessResponse({'count':count,'data':serializer.data}))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))