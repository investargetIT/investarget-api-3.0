#coding=utf-8
import threading

import datetime

from emailmanage.views import getAllProjectsNeedToSendMail, sendEmailToUser
from msg.models import schedule
from third.views.huanxin import downloadChatMessages
from timeline.models import timelineTransationStatu
from utils.sendMessage import sendmessage_schedulemsg, sendmessage_timelinealertcycleexpire


def task1_loadsendmailproj():
    class task1_Thread(threading.Thread):
        def run(self):
            getAllProjectsNeedToSendMail()
    task1_Thread().start()

def task2_sendmailprojtouser():
    class task2_Thread(threading.Thread):
        def run(self):
            sendEmailToUser()
    task2_Thread().start()

def task3_loadchatmessageandsave():
    class task3_Thread(threading.Thread):
        def run(self):
            downloadChatMessages()
    task3_Thread().start()


def task4_sendAllExpiredMsg():
    class task4_Thread(threading.Thread):
        def run(self):
            sendExpiredScheduleMsg()
            sendExpiredTimelineMsg()
    task4_Thread().start()






























def sendExpiredScheduleMsg():
    schedule_qs = schedule.objects.all().filter(is_deleted=False,
                                                scheduledtime__year=datetime.datetime.now().year,
                                                scheduledtime__month=datetime.datetime.now().month,
                                                scheduledtime__day=datetime.datetime.now().day)
    if schedule_qs.exists():
        for instance in schedule_qs:
            sendmessage_schedulemsg(instance, receiver=instance.createuser,
                                    types=['app', 'wenmsg'])
def sendExpiredTimelineMsg():
    timelineTransationStatu_qs = timelineTransationStatu.objects.all().filter(is_deleted=False,
                                                               inDate__year=datetime.datetime.now().year,
                                                               inDate__month=datetime.datetime.now().month,
                                                               inDate__day=datetime.datetime.now().day)
    if timelineTransationStatu_qs.exists():
        for instance in timelineTransationStatu_qs:
            sendmessage_timelinealertcycleexpire(instance, receiver=instance.createuser,
                                    types=['app', 'wenmsg'])