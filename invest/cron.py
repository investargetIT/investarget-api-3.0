#coding=utf-8
import threading

from emailmanage.views import getAllProjectsNeedToSendMail, sendEmailToUser
from third.views.huanxin import downloadChatMessages


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