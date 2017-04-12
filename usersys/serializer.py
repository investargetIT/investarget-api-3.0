#coding=utf-8
from django.contrib.auth.models import Group
from rest_framework import serializers

from org.serializer import OrgCommonSerializer
from .models import MyUser, UserRelation, userTags

#用户关系基本信息
class UserRelationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRelation
        fields = ('id','investoruser','traderuser','relationtype','score')

#用户关系全部信息
class UserRelationDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRelation
        fields = '__all__'
#权限组基本信息
class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id','name',)
#用户基本信息
class UserCommenSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ('id', 'groups', 'name','email','mobile','company',)

#用户全部信息
class UserSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(MyUser.groups,many=True)
    class Meta:
        model = MyUser
        fields = '__all__'
        depth = 1

#创建用户所需信息
class CreatUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ('id', 'groups', 'tags', 'name', 'mobile', 'email', 'title', 'company', 'org',)

#用户列表显示信息
class UserListSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(MyUser.groups,many=True)
    org = OrgCommonSerializer(MyUser.org)
    investor_relations = UserRelationSerializer(MyUser.investor_relations, many=True)
    class Meta:
        model = MyUser
        fields = ('id','groups','tags','name','mobile','email','title','company','org','investor_relations')
        depth = 1




