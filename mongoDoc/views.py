#coding:utf-8

import traceback

import datetime

# Create your views here.
from django.core.paginator import Paginator, EmptyPage
from mongoengine import Q
from rest_framework import viewsets

from mongoDoc.models import GroupEmailData, IMChatMessages
from mongoDoc.serializers import GroupEmailDataSerializer, IMChatMessagesSerializer
from utils.customClass import JSONResponse, InvestError
from utils.util import SuccessResponse, InvestErrorResponse, ExceptionResponse, catchexcption, logexcption, \
    loginTokenIsAvailable

APPID = '9845160'
APIKEY = 'xxnuhuvogLrRR7jCH9vKh2Tt'
APISECRET = 'pmnYqjuzEXpnzi96FbNlm4PxvWUw460y'





class GroupEmailDataView(viewsets.ModelViewSet):
    queryset = GroupEmailData.objects.all()
    serializer_class = GroupEmailDataSerializer
    def list(self, request, *args, **kwargs):
        try:
            projtitle = request.GET.get('title')
            page_size = request.GET.get('page_size')
            page_index = request.GET.get('page_index')  # 从第一页开始
            if not page_size:
                page_size = 10
            if not page_index:
                page_index = 1
            queryset = self.queryset
            sort = request.GET.get('sort')
            if projtitle:
                queryset = queryset(projtitle__icontains=projtitle)
            if sort not in ['True', 'true', True, 1, 'Yes', 'yes', 'YES', 'TRUE']:
                queryset = queryset.order_by('-savetime',)
            else:
                queryset = queryset.order_by('savetime',)
            try:
                count = queryset.count()
                queryset = Paginator(queryset, page_size)
                queryset = queryset.page(page_index)
            except EmptyPage:
                return JSONResponse(SuccessResponse({'count': 0, 'data': []}))
            serializer = GroupEmailDataSerializer(queryset,many=True)
            return JSONResponse(SuccessResponse({'count':count,'data':serializer.data}))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))


def saveSendEmailDataToMongo(data):
    serializer = GroupEmailDataSerializer(data=data)
    try:
        if serializer.is_valid():
            serializer.save()
        else:
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
    filter_fields = ('chatfrom','to')

    # @loginTokenIsAvailable()
    def list(self, request, *args, **kwargs):
        try:
            # chatto = request.GET.get('to')
            # chatfrom = str(request.user.id)
            chatto = '9'
            chatfrom = '102'
            page_size = request.GET.get('page_size')
            page_index = request.GET.get('page_index')  # 从第一页开始
            if not page_size:
                page_size = 20
            if not page_index:
                page_index = 1
            queryset = self.queryset
            sort = request.GET.get('sort')
            if chatto:
                queryset = queryset(Q(to=chatto, chatfrom=chatfrom)|Q(to=chatfrom, chatfrom=chatto))
            else:
                raise InvestError(2007, msg='to cannot be null')
            if sort not in ['True', 'true', True, 1, 'Yes', 'yes', 'YES', 'TRUE']:
                queryset = queryset.order_by('-timestamp',)
            else:
                queryset = queryset.order_by('timestamp',)
            try:
                count = queryset.count()
                queryset = Paginator(queryset, page_size)
                queryset = queryset.page(page_index)
            except EmptyPage:
                return JSONResponse(SuccessResponse({'count': 0, 'data': []}))
            serializer = self.serializer_class(queryset,many=True)
            return JSONResponse(SuccessResponse({'count':count,'data':serializer.data}))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

def saveChatMessageDataToMongo(data):
    queryset = IMChatMessages.objects.all()
    if queryset(msg_id=data['msg_id']).count() > 0:
        pass
    else:
        serializer = IMChatMessagesSerializer(data=data)
        try:
            if serializer.is_valid():
                serializer.save()
            else:
                raise InvestError(2001, msg=serializer.error_messages)
        except Exception:
            logexcption()