
from django.http import HttpResponse
from rest_framework import filters
from rest_framework.permissions import BasePermission
from rest_framework.renderers import JSONRenderer


from utils.responsecode import responsecode


class JSONResponse(HttpResponse):
    def __init__(self,data, **kwargs):
        content = JSONRenderer().render(data=data)
        kwargs['content_type'] = 'application/json; charset=utf-8'
        super(JSONResponse, self).__init__(content , **kwargs)

class InvestError(Exception):
    def __init__(self, code,msg=None):
        self.code = code
        if msg:
            self.msg = msg
        else:
            self.msg = responsecode[str(code)]

class IsSuperUser(BasePermission):
    """
    Allows access only to admin users.
    """

    def has_permission(self, request, view):
        return (
            request.method in ('GET', 'HEAD', 'OPTIONS') or
            request.user and
            request.user.is_superuser
        )

# class AppThread(threading.Thread):
#     def __init__(self,content, receiver_alias, platform, bdage, n_extras):
#         self.content = content
#         self.receiver_alias = receiver_alias
#         self.platform = platform
#         self.bdage = bdage
#         self.n_extras = n_extras
#         threading.Thread.__init__(self)
#     def run (self):
#         data_dict = {
#             'receiver_alias': self.receiver_alias,
#             'content': self.content,
#             'platform': self.platform,
#             'bdage': self.bdage,
#             'n_extras': self.n_extras,
#         }
#         return pushnotification(data_dict)
#
# class EmailThread(threading.Thread):
#     def __init__(self,destination,projectsign,vars=None):
#         self.destination = destination
#         self.projectsign = projectsign
#         self.vars = vars
#         threading.Thread.__init__(self)
#     def run (self):
#         return xsendEmail(self.destination,self.projectsign,self.vars)
#
# class SmsThread(threading.Thread):
#     def __init__(self,destination,projectsign,vars=None):
#         self.destination = destination
#         self.projectsign = projectsign
#         self.vars = vars
#         threading.Thread.__init__(self)
#     def run (self):
#         return xsendSms(self.destination,self.projectsign,self.vars)
#
#
# # class WebMsgThread(threading.Thread):
# #     def __init__(self,content, messagetype, title, receiver, sender):
# #         self.content = content
# #         self.messagetype = messagetype
# #         self.title = title
# #         self.receiver = receiver
# #         self.sender = sender
# #         threading.Thread.__init__(self)
# #     def run (self):
# #         return saveMessage(self.content, self.messagetype, self.title, self.receiver, self.sender)