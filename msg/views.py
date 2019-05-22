#coding=utf-8
import traceback

import datetime

import requests
from django.core.paginator import Paginator, EmptyPage
from django.db import transaction

# Create your views here.
from django.db.models import Q
from rest_framework import filters
from rest_framework import viewsets

from msg.models import message, schedule, webexUser, webexMeeting
from msg.serializer import MsgSerializer, ScheduleSerializer, ScheduleCreateSerializer, WebEXUserSerializer, \
    WebEXMeetingSerializer, ScheduleMeetingSerializer
from third.thirdconfig import webEX_siteName, webEX_webExID, webEX_password
from utils.customClass import InvestError, JSONResponse
from utils.util import logexcption, loginTokenIsAvailable, SuccessResponse, InvestErrorResponse, ExceptionResponse, \
    catchexcption, returnListChangeToLanguage, returnDictChangeToLanguage, mySortQuery, checkSessionToken
import xml.etree.cElementTree as ET

def saveMessage(content,type,title,receiver,sender=None,modeltype=None,sourceid=None):
    try:
        data = {}
        data['content'] = content
        data['messagetitle'] = title
        data['type'] = type
        data['receiver'] = receiver.id
        data['datasource'] = receiver.datasource_id
        if modeltype:
            data['sourcetype'] = modeltype
        if sourceid:
            data['sourceid'] = sourceid
        if sender:
            data['sender'] = sender.id
        msg = MsgSerializer(data=data)
        if msg.is_valid():
            msg.save()
        else:
            raise InvestError(code=20019)
        return msg.data
    except InvestError as err:
        logexcption()
        return err.msg
    except Exception as err:
        logexcption()
        return err.message


class WebMessageView(viewsets.ModelViewSet):
    """
    list:获取站内信列表
    update:已读回执
    """
    filter_backends = (filters.DjangoFilterBackend,)
    queryset = message.objects.all().filter(is_deleted=False)
    filter_fields = ('datasource','type','isRead','receiver')
    serializer_class = MsgSerializer


    @loginTokenIsAvailable()
    def list(self, request, *args, **kwargs):
        try:
            page_size = request.GET.get('page_size', 10)
            page_index = request.GET.get('page_index', 1)
            lang = request.GET.get('lang', 'cn')
            queryset = self.filter_queryset(self.get_queryset()).filter(receiver=request.user.id).order_by('-createdtime',)
            try:
                count = queryset.count()
                queryset = Paginator(queryset, page_size)
                queryset = queryset.page(page_index)
            except EmptyPage:
                return JSONResponse(SuccessResponse({'count': 0, 'data': []}))
            serializer = MsgSerializer(queryset, many=True)
            return JSONResponse(SuccessResponse({'count':count,'data':serializer.data}))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable()
    def update(self, request, *args, **kwargs):
        try:
            msg = self.get_object()
            if msg.receiver.id != request.user.id:
                raise InvestError(2009)
            with transaction.atomic():
                data = {
                    'isRead':True,
                    'readtime':datetime.datetime.now(),
                }
                msgserializer = MsgSerializer(msg, data=data)
                if msgserializer.is_valid():
                    msgserializer.save()
                else:
                    raise InvestError(code=20071,msg='data有误_%s' % msgserializer.errors)
                return JSONResponse(SuccessResponse(msgserializer.data))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))


class WebEXMeetingView(viewsets.ModelViewSet):
    """
        list: 视频会议列表
        create: 新增视频会议
        retrieve: 查看某一视频会议
        update: 修改某一视频会议信息
        destroy: 删除某一视频会议
        """
    filter_backends = (filters.SearchFilter, filters.DjangoFilterBackend,)
    queryset = webexMeeting.objects.all().filter(is_deleted=False)
    filter_fields = ('title', 'meetingKey', 'createuser')
    search_fields = ('startDate', 'createuser__usernameC', 'createuser__usernameE')
    serializer_class = WebEXMeetingSerializer
    webex_url = 'https://investarget.webex.com.cn/WBXService/XMLService'

    @loginTokenIsAvailable()
    def list(self, request, *args, **kwargs):
        try:
            page_size = request.GET.get('page_size', 10)
            page_index = request.GET.get('page_index', 1)
            lang = request.GET.get('lang', 'cn')
            queryset = self.filter_queryset(self.queryset.filter(datasource_id=request.user.datasource_id))
            sortfield = request.GET.get('sort', 'startDate')
            desc = request.GET.get('desc', 0)
            queryset = mySortQuery(queryset, sortfield, desc)
            try:
                count = queryset.count()
                queryset = Paginator(queryset, page_size)
                queryset = queryset.page(page_index)
            except EmptyPage:
                return JSONResponse(SuccessResponse({'count': 0, 'data': []}))
            serializer = self.serializer_class(queryset, many=True)
            return JSONResponse(SuccessResponse({'count':count,'data':returnListChangeToLanguage(serializer.data, lang)}))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable()
    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            data['createuser'] = request.user.id
            with transaction.atomic():
                instanceSerializer = self.serializer_class(data=data)
                if instanceSerializer.is_valid():
                    instance = instanceSerializer.save()
                else:
                    raise InvestError(code=20071, msg='参数错误：%s' % instanceSerializer.errors)
                data['startDate'] = instance.startDate.strftime('%m/%d/%Y %H:%M:%S')
                XML_body = getCreateXMLBody(data)
                s = requests.post(url=self.webex_url, data=XML_body.encode("utf-8"))
                if s.status_code == 200:
                    res = ET.fromstring(s.text)
                    result = next(res.iter('{http://www.webex.com/schemas/2002/06/service}result')).text
                    if result == 'FAILURE':
                        reason = next(res.iter('{http://www.webex.com/schemas/2002/06/service}reason')).text
                        raise InvestError(8006, msg=reason)
                    else:
                        meetingkey = next(res.iter('{http://www.webex.com/schemas/2002/06/service/meeting}meetingkey')).text
                        serv_host = next(res.iter('{http://www.webex.com/schemas/2002/06/service}host')).text
                        serv_attendee = next(res.iter('{http://www.webex.com/schemas/2002/06/service}attendee')).text
                        meetGuestToken = next(res.iter('{http://www.webex.com/schemas/2002/06/service/meeting}guestToken')).text
                        meetingData = {'meetingKey': meetingkey, 'url_host': serv_host, 'url_attendee': serv_attendee,
                                  'guestToken': meetGuestToken}
                        newInstanceSerializer = self.serializer_class(instance, data=meetingData)
                        if newInstanceSerializer.is_valid():
                            newInstanceSerializer.save()
                else:
                    raise InvestError(8006, msg=s.text)
            return JSONResponse(SuccessResponse(instanceSerializer.data))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))


    @loginTokenIsAvailable()
    def retrieve(self, request, *args, **kwargs):
        try:
            lang = request.GET.get('lang')
            instance = self.get_object()
            serializer = self.serializer_class(instance)
            return JSONResponse(SuccessResponse(returnDictChangeToLanguage(serializer.data, lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable()
    def update(self, request, *args, **kwargs):
        try:
            lang = request.GET.get('lang')
            instance = self.get_object()
            data = request.data
            with transaction.atomic():
                instanceSerializer = self.serializer_class(instance, data=data)
                if instanceSerializer.is_valid():
                    instanceSerializer.save()
                else:
                    raise InvestError(code=20071, msg='参数错误：%s' % instanceSerializer.errors)
            data['startDate'] = instance.startDate.strftime('%m/%d/%Y %H:%M:%S')
            XML_body = getUpdateXMLBody(instance.meetingKey, data)
            s = requests.post(url=self.webex_url, data=XML_body.encode("utf-8"))
            if s.status_code != 200:
                raise InvestError(8006, msg=s.text)
            else:
                res = ET.fromstring(s.text)
                result = next(res.iter('{http://www.webex.com/schemas/2002/06/service}result')).text
                if result == 'FAILURE':
                    reason = next(res.iter('{http://www.webex.com/schemas/2002/06/service}reason')).text
                    raise InvestError(8006, msg=reason)
                else:
                    serv_host = next(res.iter('{http://www.webex.com/schemas/2002/06/service}host')).text
                    serv_attendee = next(res.iter('{http://www.webex.com/schemas/2002/06/service}attendee')).text
                    meetingData = {'url_host': serv_host, 'url_attendee': serv_attendee,}
                    with transaction.atomic():
                        instanceSerializer = self.serializer_class(instance, data=meetingData)
                        if instanceSerializer.is_valid():
                            instanceSerializer.save()
                        else:
                            raise InvestError(code=20071, msg='参数错误：%s' % instanceSerializer.errors)
                    return JSONResponse(SuccessResponse(returnDictChangeToLanguage(instanceSerializer.data, lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable()
    def destroy(self, request, *args, **kwargs):
        try:
            lang = request.GET.get('lang')
            instance = self.get_object()
            XML_body = getDeleteXMLBody(instance.meetingKey)
            s = requests.post(url=self.webex_url, data=XML_body.encode("utf-8"))
            if s.status_code != 200:
                raise InvestError(8006, msg=s.text)
            else:
                res = ET.fromstring(s.text)
                result = next(res.iter('{http://www.webex.com/schemas/2002/06/service}result')).text
                if result == 'FAILURE':
                    reason = next(res.iter('{http://www.webex.com/schemas/2002/06/service}reason')).text
                    raise InvestError(8006, msg=reason)
                else:
                    with transaction.atomic():
                        instance.is_deleted = True
                        instance.deleteduser = request.user
                        instance.deletedtime = datetime.datetime.now()
                        instance.save()
                    return JSONResponse(SuccessResponse(returnDictChangeToLanguage(self.serializer_class(instance).data, lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

def getXMLHeaders():
    headers = """
                         <header>
                             <securityContext>
                                 <siteName>{siteName}</siteName>
                                 <webExID>{webExID}</webExID>
                                 <password>{password}</password>
                             </securityContext>
                         </header>
             """.format(siteName=webEX_siteName, webExID=webEX_webExID, password=webEX_password)
    return headers

def getCreateXMLBody(data):
    headers = getXMLHeaders()
    meetingPassword = data.get('password', 'Aa123456')  # 会议密码
    title = data.get('title', '')  # 会议名称
    agenda = data.get('agenda', '议程暂无')  # 会议议程
    startDate = data.get('startDate', '')  # 会议开始时间（格式：11/30/2015 10:00:00）
    duration = data.get('duration', '60')  # 会议持续时间（单位：分钟）
    XML_body = """
                               <?xml version="1.0" encoding="UTF-8"?>
                               <serv:message xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
                                   {headers}
                                   <body>
                                       <bodyContent xsi:type="java:com.webex.service.binding.meeting.CreateMeeting">
                                           <accessControl>
                                               <meetingPassword>{meetingPassword}</meetingPassword>
                                           </accessControl>
                                           <metaData>
                                               <confName>{title}</confName>
                                               <agenda>{agenda}</agenda>
                                           </metaData>
                                           <schedule>
                                               <startDate>{startDate}</startDate>
                                               <duration>{duration}</duration>
                                           </schedule>
                                       </bodyContent>
                                   </body>
                               </serv:message>
                           """.format(headers=headers, meetingPassword=meetingPassword, title=title, agenda=agenda,
                                      startDate=startDate, duration=duration)
    return XML_body


def getGetXMLBody(meetingKey):
    headers = getXMLHeaders()
    XML_body = """
                            <?xml version="1.0" encoding="UTF-8"?>
                            <serv:message xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
                                {headers}
                                <body>
                                    <bodyContent xsi:type="java:com.webex.service.binding.meeting.GetMeeting">
                                        <meetingKey>{meetingKey}</meetingKey>
                                    </bodyContent>
                                </body>
                            </serv:message>
                        """.format(headers=headers, meetingKey=meetingKey)
    return XML_body

def get_hostKey(meetingKey):
    XML_body = getGetXMLBody(meetingKey)
    webex_url = 'https://investarget.webex.com.cn/WBXService/XMLService'
    s = requests.post(url=webex_url, data=XML_body.encode("utf-8"))
    if s.status_code != 200:
        raise InvestError(8006, msg=s.text)
    else:
        res = ET.fromstring(s.text)
        hostKey = next(res.iter('{http://www.webex.com/schemas/2002/06/service/meeting}hostKey')).text
        return hostKey

def getUpdateXMLBody(meetingKey, data):
    headers = getXMLHeaders()
    password = '<meetingPassword>{}</meetingPassword>'.format(data['password']) if data.get('password') else ''  # 会议密码
    confName = '<confName>{}</confName>'.format(data['title']) if data.get('title') else ''  # 会议名称
    agenda = '<agenda>{}</agenda>'.format(data['agenda']) if data.get('agenda') else ''  # 会议议程
    startDate = '<startDate>{}</startDate>'.format(data['startDate']) if data.get('startDate') else ''  # 会议开始时间
    duration = '<duration>{}</duration>'.format(data['duration']) if data.get('duration') else ''  # 会议持续时间
    XML_body = """
                                <?xml version="1.0" encoding="UTF-8"?>
                                <serv:message xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
                                    {headers}
                                    <body>
                                        <bodyContent xsi:type="java:com.webex.service.binding.meeting.SetMeeting">
                                            <meetingkey>{meetingKey}</meetingkey>
                                            <accessControl>
                                                {meetingPassword}
                                            </accessControl>
                                            <metaData>
                                                {confName}
                                                {agenda}
                                            </metaData>
                                            <schedule>
                                                {startDate}
                                                {duration}
                                            </schedule>
                                        </bodyContent>
                                    </body>
                                </serv:message>
                            """.format(headers=headers, meetingKey=meetingKey, meetingPassword=password,
                                       confName=confName, agenda=agenda, startDate=startDate, duration=duration)
    return XML_body

def getDeleteXMLBody(meetingKey):
    headers = getXMLHeaders()
    XML_body = """
                            <?xml version="1.0" encoding="UTF-8"?>
                            <serv:message xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
                                {headers}
                                <body>
                                    <bodyContent xsi:type="java:com.webex.service.binding.meeting.DelMeeting">
                                        <meetingKey>{meetingKey}</meetingKey>
                                    </bodyContent>
                                </body>
                            </serv:message>
                        """.format(headers=headers, meetingKey=meetingKey)
    return XML_body


def createWebEXMeeting(data):
    webex_url = 'https://investarget.webex.com.cn/WBXService/XMLService'
    with transaction.atomic():
        instanceSerializer = WebEXMeetingSerializer(data=data)
        if instanceSerializer.is_valid():
            instance = instanceSerializer.save()
        else:
            raise InvestError(code=20071, msg='创建会议参数错误：%s' % instanceSerializer.errors)
        data['startDate'] = instance.startDate.strftime('%m/%d/%Y %H:%M:%S')
        XML_body = getCreateXMLBody(data)
        s = requests.post(url=webex_url, data=XML_body.encode("utf-8"))
        if s.status_code == 200:
            res = ET.fromstring(s.text)
            result = next(res.iter('{http://www.webex.com/schemas/2002/06/service}result')).text
            if result == 'FAILURE':
                reason = next(res.iter('{http://www.webex.com/schemas/2002/06/service}reason')).text
                raise InvestError(8006, msg=reason)
            else:
                meetingkey = next(res.iter('{http://www.webex.com/schemas/2002/06/service/meeting}meetingkey')).text
                serv_host = next(res.iter('{http://www.webex.com/schemas/2002/06/service}host')).text
                serv_attendee = next(res.iter('{http://www.webex.com/schemas/2002/06/service}attendee')).text
                meetGuestToken = next(res.iter('{http://www.webex.com/schemas/2002/06/service/meeting}guestToken')).text
                hostKey = get_hostKey(meetingkey)
                meetingData = {'meetingKey': meetingkey, 'url_host': serv_host, 'url_attendee': serv_attendee,
                               'guestToken': meetGuestToken, 'hostKey': hostKey}
                newInstanceSerializer = WebEXMeetingSerializer(instance, data=meetingData)
                if newInstanceSerializer.is_valid():
                    newInstance = newInstanceSerializer.save()
                else:
                    raise InvestError(code=20071, msg='会议信息错误：%s' % instanceSerializer.errors)
        else:
            raise InvestError(8006, msg=s.text)
        return newInstance



class ScheduleView(viewsets.ModelViewSet):
    """
        list:日程安排列表
        create:新建日程
        retrieve:查看某一日程安排信息
        update:修改日程安排信息
        destroy:删除日程安排
        """
    filter_backends = (filters.SearchFilter, filters.DjangoFilterBackend,)
    queryset = schedule.objects.all().filter(is_deleted=False)
    filter_fields = ('proj', 'createuser', 'user', 'projtitle', 'country', 'manager')
    search_fields = ('createuser__usernameC', 'user__usernameC', 'user__mobile', 'proj__projtitleC', 'proj__projtitleE')
    serializer_class = ScheduleSerializer


    @loginTokenIsAvailable()
    def list(self, request, *args, **kwargs):
        try:
            page_size = request.GET.get('page_size', 10)
            page_index = request.GET.get('page_index', 1)
            lang = request.GET.get('lang', 'cn')
            date = request.GET.get('date')
            time = request.GET.get('time')
            queryset = self.filter_queryset(self.queryset.filter(datasource_id=request.user.datasource_id))
            if date:
                date = datetime.datetime.strptime(date.encode('utf-8'), "%Y-%m-%d")
                queryset = queryset.filter(scheduledtime__year=date.year,scheduledtime__month=date.month)
            if time:
                time = datetime.datetime.strptime(time.encode('utf-8'), "%Y-%m-%dT%H:%M:%S")
                queryset = queryset.filter(scheduledtime__gt=time)
            if request.user.has_perm('msg.admin_manageSchedule'):
                queryset = queryset
            else:
                queryset = queryset.filter(Q(manager_id=request.user.id) | Q(createuser_id=request.user.id))
            sortfield = request.GET.get('sort', 'scheduledtime')
            desc = request.GET.get('desc', 0)
            queryset = mySortQuery(queryset, sortfield, desc)
            try:
                count = queryset.count()
                queryset = Paginator(queryset, page_size)
                queryset = queryset.page(page_index)
            except EmptyPage:
                return JSONResponse(SuccessResponse({'count': 0, 'data': []}))
            serializer = ScheduleSerializer(queryset, many=True)
            return JSONResponse(SuccessResponse({'count':count,'data':returnListChangeToLanguage(serializer.data, lang)}))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))


    @loginTokenIsAvailable()
    def create(self, request, *args, **kwargs):
        try:
            # checkSessionToken(request)
            data = request.data
            map(lambda x: x.update({'createuser': request.user.id,
                                    'manager': request.user.id if not x.get('manager') else x['manager']
                                    }), data)
            with transaction.atomic():
                for i in range(0, len(data)):
                    if data[i]['type'] == 4 and not data[i].get('meeting'):
                        data[i]['startDate'] = data[i]['scheduledtime']
                        meetingInstance = createWebEXMeeting(data[i])
                        data[i]['meeting'] = meetingInstance.id
                scheduleserializer = ScheduleCreateSerializer(data=data, many=True)
                if scheduleserializer.is_valid():
                    instances = scheduleserializer.save()
                else:
                    raise InvestError(code=20071, msg='参数错误：%s' % scheduleserializer.errors)
                return JSONResponse(SuccessResponse(ScheduleMeetingSerializer(instances, many=True).data))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable()
    def retrieve(self, request, *args, **kwargs):
        try:
            lang = request.GET.get('lang')
            instance = self.get_object()
            if request.user.has_perm('msg.admin_manageSchedule'):
                pass
            elif request.user in [instance.createuser, instance.manager]:
                pass
            else:
                raise InvestError(code=2009)
            serializer = ScheduleSerializer(instance)
            return JSONResponse(SuccessResponse(returnDictChangeToLanguage(serializer.data, lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable()
    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            if request.user.has_perm('msg.admin_manageSchedule'):
                pass
            elif request.user in [instance.createuser, instance.manager]:
                pass
            else:
                raise InvestError(code=2009)
            data = request.data
            data['lastmodifyuser'] = request.user.id
            with transaction.atomic():
                scheduleserializer = ScheduleCreateSerializer(instance, data=data)
                if scheduleserializer.is_valid():
                    newinstance = scheduleserializer.save()
                else:
                    raise InvestError(code=20071, msg='参数错误：%s' % scheduleserializer.errors)
                return JSONResponse(SuccessResponse(ScheduleSerializer(newinstance).data))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable()
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            if request.user.has_perm('msg.admin_manageSchedule'):
                pass
            elif request.user in [instance.createuser, instance.manager]:
                pass
            else:
                raise InvestError(code=2009)
            with transaction.atomic():
                instance.is_deleted = True
                instance.deleteduser = request.user
                instance.deletedtime = datetime.datetime.now()
                instance.save()
                return JSONResponse(SuccessResponse(ScheduleCreateSerializer(instance).data))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))


class WebEXUserView(viewsets.ModelViewSet):
    """
        list: 视频会议参会人员列表
        create: 新增视频会议参会人员
        retrieve: 查看某一视频会议参会人员
        update: 修改某一视频会议参会人员信息
        destroy: 删除某一视频会议参会人员
        """
    filter_backends = (filters.SearchFilter, filters.DjangoFilterBackend,)
    queryset = webexUser.objects.all().filter(is_deleted=False)
    filter_fields = ('user', 'name', 'email', 'meeting', 'meetingRole')
    search_fields = ('meeting__startDate', 'user__usernameC', 'user__usernameE', 'name', 'email')
    serializer_class = WebEXUserSerializer


    @loginTokenIsAvailable()
    def list(self, request, *args, **kwargs):
        try:
            page_size = request.GET.get('page_size', 10)
            page_index = request.GET.get('page_index', 1)
            lang = request.GET.get('lang', 'cn')
            queryset = self.filter_queryset(self.queryset.filter(datasource_id=request.user.datasource_id))
            sortfield = request.GET.get('sort', 'lastmodifytime')
            desc = request.GET.get('desc', 0)
            queryset = mySortQuery(queryset, sortfield, desc)
            try:
                count = queryset.count()
                queryset = Paginator(queryset, page_size)
                queryset = queryset.page(page_index)
            except EmptyPage:
                return JSONResponse(SuccessResponse({'count': 0, 'data': []}))
            serializer = self.serializer_class(queryset, many=True)
            return JSONResponse(SuccessResponse({'count':count,'data':returnListChangeToLanguage(serializer.data, lang)}))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))


    @loginTokenIsAvailable()
    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            map(lambda x: x.update({'createuser': request.user.id}), data)
            with transaction.atomic():
                instanceSerializer = self.serializer_class(data=data, many=True)
                if instanceSerializer.is_valid():
                    instanceSerializer.save()
                else:
                    raise InvestError(code=20071, msg=instanceSerializer.errors)
                return JSONResponse(SuccessResponse(returnDictChangeToLanguage(instanceSerializer.data)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            # catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable()
    def retrieve(self, request, *args, **kwargs):
        try:
            lang = request.GET.get('lang')
            instance = self.get_object()
            serializer = self.serializer_class(instance)
            return JSONResponse(SuccessResponse(returnDictChangeToLanguage(serializer.data, lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable()
    def update(self, request, *args, **kwargs):
        try:
            lang = request.GET.get('lang')
            instance = self.get_object()
            data = request.data
            with transaction.atomic():
                instanceSerializer = self.serializer_class(instance, data=data)
                if instanceSerializer.is_valid():
                    newinstance = instanceSerializer.save()
                else:
                    raise InvestError(code=20071, msg='参数错误：%s' % instanceSerializer.errors)
                return JSONResponse(SuccessResponse(returnDictChangeToLanguage(instanceSerializer.data, lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable()
    def destroy(self, request, *args, **kwargs):
        try:
            lang = request.GET.get('lang')
            instance = self.get_object()
            with transaction.atomic():
                instance.is_deleted = True
                instance.deleteduser = request.user
                instance.deletedtime = datetime.datetime.now()
                instance.save()
                return JSONResponse(SuccessResponse(returnDictChangeToLanguage(self.serializer_class(instance).data, lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))