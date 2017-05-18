from django.shortcuts import render

# Create your views here.
from msg.models import message
from msg.serializer import MsgSerializer
from utils.customClass import InvestError
from utils.util import logexcption






def saveMessage(content,type,title,receiver,sender=None):
    try:
        data = {}
        data['content'] = content
        data['title'] = title
        data['type'] = type.id
        data['receiver'] = receiver.id
        data['datasource'] = receiver.datasource_id
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

