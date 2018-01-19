import datetime

import operator
from django.db import models
from django.http import HttpResponse
from django.utils import six
from qiniu.services.storage.upload_progress_recorder import UploadProgressRecorder
from rest_framework import throttling
from rest_framework.compat import is_authenticated, distinct
from rest_framework.filters import SearchFilter
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

class RelationFilter(Filter):
    def __init__(self, filterstr,lookup_method='exact',relationName=None, **kwargs):
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

class MySearchFilter(SearchFilter):
    def filter_queryset(self, request, queryset, view):
        search_fields = getattr(view, 'search_fields', None)
        search_terms = self.get_search_terms(request)

        if not search_fields or not search_terms:
            return queryset

        orm_lookups = [
            self.construct_search(six.text_type(search_field))
            for search_field in search_fields
            ]

        qslist = []
        for search_term in search_terms:
            queries = [
                models.Q(**{orm_lookup: search_term})
                for orm_lookup in orm_lookups
                ]
            qs = queryset.filter(reduce(operator.or_, queries))
            qslist.append(qs)
        queryset = reduce(lambda x,y:x|y,qslist).distinct()
        return queryset


class AppEventRateThrottle(throttling.SimpleRateThrottle):
    scope = 'rw_mongodata'

    def get_cache_key(self, request, view):
        if is_authenticated(request.user):
            ident = request.user.pk
        else:
            ident = self.get_ident(request)

        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }

class MyModel(models.Model):
    lastmodifytime = models.DateTimeField(blank=True, null=True)
    createdtime = models.DateTimeField(blank=True, null=True)
    deletedtime = models.DateTimeField(blank=True, null=True)
    is_deleted = models.BooleanField(blank=True, default=False)

    class Meta:
        abstract = True

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.pk is None:
            self.createdtime = datetime.datetime.now()
        self.lastmodifytime = datetime.datetime.now()
        super(MyModel,self).save(force_insert, force_update, using, update_fields)

class MyForeignKey(models.ForeignKey):
    def __init__(self, to, on_delete=None, related_name=None, related_query_name=None,
                 limit_choices_to=None, parent_link=False, to_field=None,
                 db_constraint=True, **kwargs):
        if kwargs.get('null'):
            if on_delete:
                pass
            else:
                on_delete = models.SET_NULL
        super(MyForeignKey, self).__init__(to,on_delete=on_delete,related_name=related_name,related_query_name=related_query_name,
                                           limit_choices_to=limit_choices_to,parent_link=parent_link,to_field=to_field,db_constraint=db_constraint,**kwargs)

    def get_extra_descriptor_filter(self,instance):
        # if hasattr(instance,'is_deleted'):
        #     return {'is_deleted':False}
        return {}


class MyUploadProgressRecorder(UploadProgressRecorder):
    def __init__(self):
        self.record_folder = APILOG_PATH['qiniuuploadprogresspath']
    #
    def get_upload_record(self, file_name, key):
        key = '{0}.{1}.doc'.format(key,'p')
        key = base64.urlsafe_b64encode(key.encode('utf-8'))
        upload_record_file_path = os.path.join(self.record_folder,
                                               key)
        if not os.path.isfile(upload_record_file_path):
            return None
        with open(upload_record_file_path, 'r') as f:
            json_data = json.load(f)
        return json_data

    def set_upload_record(self, file_name, key, data):
        key = '{0}.{1}.doc'.format(key, 'p')
        key = base64.urlsafe_b64encode(key.encode('utf-8'))
        upload_record_file_path = os.path.join(self.record_folder, key)
        with open(upload_record_file_path, 'w') as f:
            json.dump(data, f)

    def delete_upload_record(self, file_name, key):
        key = '{0}.{1}.doc'.format(key, 'p')
        key = base64.urlsafe_b64encode(key.encode('utf-8'))
        record_file_path = os.path.join(self.record_folder,
                                        key)
        os.remove(record_file_path)

class MyManyToManyField(models.ManyToManyField):
    # def set_attributes_from_rel(self):
    #     pass
    pass
