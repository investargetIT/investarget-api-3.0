from django.shortcuts import render

# Create your views here.
from msg.models import message
from utils.util import logexcption






def saveMessage(content,type,title,receiver,sender=None):
    try:
        msg = message()
        msg.content = content
        msg.title = title
        msg.type_id = type
        msg.receiver = receiver
        if sender:
            msg.sender = sender
        msg.save()
        return message
    except:
        logexcption()
        return None


