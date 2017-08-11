from django.db import models
from django.http import HttpResponse
from qiniu.services.storage.upload_progress_recorder import UploadProgressRecorder
from rest_framework.permissions import BasePermission
from rest_framework.renderers import JSONRenderer

from invest.settings import APILOG_PATH
from utils.responsecode import responsecode
from django_filters import Filter
import json
import os
import base64

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
            (request.user and
            request.user.is_superuser)
        )
class RelationFilter(Filter):
    def __init__(self, filterstr,lookup_method,relationName=None, **kwargs):
        self.filterstr = filterstr
        self.lookup_method = lookup_method
        self.relationName = relationName
        super(RelationFilter,self).__init__(**kwargs)
    def filter(self, qs, value):
        if value in ([], (), {}, '', None):
            return qs
        if value in (u'true','true'):
            value = True
        if value in (u'false','false'):
            value = False
        if self.lookup_method == 'in':
            value = value.split(',')
        if self.relationName is not None:
            return qs.filter(**{'%s__%s' % (self.filterstr,self.lookup_method): value, self.relationName:False}).distinct()
        else:
            return qs.filter(**{'%s__%s' % (self.filterstr, self.lookup_method): value}).distinct()



class MyForeignKey(models.ForeignKey):
    def get_extra_descriptor_filter(self,instance):
        if hasattr(instance,'is_deleted'):
            return {'is_deleted':False}
        return {}



class MyUploadProgressRecorder(UploadProgressRecorder):
    def __init__(self):
        self.record_folder = APILOG_PATH['qiniuuploadprogresspath']
    #
    def get_upload_record(self, file_name, key):
        if len(file_name) > 5:
            file_name = file_name[0:4]
        key = '{0}.{1}.doc'.format(key,file_name)
        key = base64.urlsafe_b64encode(key.encode('utf-8'))
        upload_record_file_path = os.path.join(self.record_folder,
                                               key)
        if not os.path.isfile(upload_record_file_path):
            return None
        with open(upload_record_file_path, 'r') as f:
            json_data = json.load(f)
        return json_data

    def set_upload_record(self, file_name, key, data):
        if len(file_name) > 5:
            file_name = file_name[0:4]
        key = '{0}.{1}.doc'.format(key, file_name)
        key = base64.urlsafe_b64encode(key.encode('utf-8'))
        upload_record_file_path = os.path.join(self.record_folder, key)
        with open(upload_record_file_path, 'w') as f:
            json.dump(data, f)

    def delete_upload_record(self, file_name, key):
        if len(file_name) > 5:
            file_name = file_name[0:4]
        key = '{0}.{1}.doc'.format(key, file_name)
        key = base64.urlsafe_b64encode(key.encode('utf-8'))
        record_file_path = os.path.join(self.record_folder,
                                        key)
        os.remove(record_file_path)

class MyManyToManyField(models.ManyToManyField):
    # def set_attributes_from_rel(self):
    #     pass
    pass
