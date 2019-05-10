#coding=utf-8
import traceback

import requests
from rest_framework.decorators import api_view

from third.thirdconfig import webEX_siteName, webEX_webExID, webEX_password
import xml.etree.cElementTree as ET

from utils.customClass import JSONResponse, InvestError
from utils.util import SuccessResponse, InvestErrorResponse, ExceptionResponse


@api_view(['POST'])
def createWebEXMeeting(request):
    """
    创建视频会议
    """
    try:
        data = request.data
        meetingPassword = data.get('meetingPassword', 'Aa123456')   # 会议密码
        confName = data.get('confName', 'Test Meeting')             # 会议名称
        agenda = data.get('agenda', 'Test')                         # 会议议程
        startDate = data.get('startDate', '5/30/2019 10:00:00')     # 会议开始时间（格式：11/30/2015 10:00:00）
        duration = data.get('duration', '60')                       # 会议持续时间（单位：分钟）
        XML_body = """
            <?xml version="1.0" encoding="UTF-8"?>
            <serv:message xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
                <header>
                    <securityContext>
                        <siteName>{siteName}</siteName>
                        <webExID>{webExID}</webExID>
                        <password>{password}</password>
                    </securityContext>
                </header>
                <body>
                    <bodyContent xsi:type="java:com.webex.service.binding.meeting.CreateMeeting">
                        <accessControl>
                            <meetingPassword>{meetingPassword}</meetingPassword>
                        </accessControl>
                        <metaData>
                            <confName>{confName}</confName>
                            <agenda>{agenda}</agenda>
                        </metaData>
                        <schedule>
                            <startDate>{startDate}</startDate>
                            <duration>{duration}</duration>
                        </schedule>
                    </bodyContent>
                </body>
            </serv:message>
        """.format(siteName=webEX_siteName, webExID=webEX_webExID, password=webEX_password,
                   meetingPassword=meetingPassword, confName=confName, agenda=agenda,
                   startDate=startDate, duration=duration)
        url = 'https://investarget.webex.com.cn/WBXService/XMLService'
        s = requests.post(url=url, data=XML_body.encode("utf-8"))
        if s.status_code == 200:
            res = ET.fromstring(s.text)
            meetingkey = next(res.iter('{http://www.webex.com/schemas/2002/06/service/meeting}meetingkey')).text
            serv_host = next(res.iter('{http://www.webex.com/schemas/2002/06/service}host')).text
            serv_attendee = next(res.iter('{http://www.webex.com/schemas/2002/06/service}attendee')).text
            meet_guestToken = next(res.iter('{http://www.webex.com/schemas/2002/06/service/meeting}guestToken')).text
            result = {'meetingkey': meetingkey, 'serv_host': serv_host, 'serv_attendee': serv_attendee, 'meet_guestToken': meet_guestToken, }
        else:
            raise InvestError(8006, msg=s.text)
        return JSONResponse(SuccessResponse(result))
    except InvestError as err:
        return JSONResponse(InvestErrorResponse(err))
    except Exception:
        return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))