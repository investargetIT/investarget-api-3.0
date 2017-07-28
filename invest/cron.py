#coding=utf-8
import threading

from emailmanage.views import getAllProjectsNeedToSendMail, sendEmailToUser


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