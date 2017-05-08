#coding=utf-8
import traceback
from rest_framework import viewsets

from sourcetype.models import Tag
from sourcetype.serializer import tagSerializer
from utils.myClass import IsSuperUser



class TagView(viewsets.ModelViewSet):
    """
    list:获取所有标签
    create:新增标签
    update:修改标签
    destroy:删除标签
    """
    permission_classes = (IsSuperUser,)
    queryset = Tag.objects.all().filter(is_deleted=False)
    serializer_class = tagSerializer





