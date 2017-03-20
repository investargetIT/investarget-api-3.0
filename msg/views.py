from django.shortcuts import render

# Create your views here.
from msg.models import message
from utils.util import logexcption






def saveMessage(content,type,title,receiver,sender=None):
    try:
        msg = message()
        msg.content = content
        msg.title = title
        msg.type = type
        msg.receiver_id = receiver
        if sender:
            msg.sender_id = sender
        msg.save()
        return message
    except:
        logexcption()
        return None


def sendmessage(message,paths):
    receiveruser = message.receiver
    for path in paths:
        if path == 'email':
            pass
        if path == 'message':
            pass
        if path == 'notification':
            pass

