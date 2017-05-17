#coding=utf-8
from django.contrib.auth.models import Group
from rest_framework import serializers

from org.serializer import OrgCommonSerializer
from .models import MyUser, UserRelation, UserFriendship


#投资人交易师关系基本信息
class UserRelationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRelation
        fields = ('id','investoruser','traderuser','relationtype','score','datasource')
        read_only_fields = ('datasource',)

#用户关系全部信息
class UserRelationDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRelation
        fields = '__all__'

# 用户好友关系基本信息
class UserFriendshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFriendship
        fields = ('id', 'user', 'friend', 'isaccept','datasource')
        read_only_fields = ('datasource',)

# 用户好友关系全部信息
class UserFriendshipDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFriendship
        fields = '__all__'

# 用户好友关系修改信息
class UserFriendshipUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFriendship
        fields = '__all__'
        read_only_fields = ('datasource','user','friend','createtime','createuser','is_deleted')

#权限组基本信息
class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id','name',)

# 权限组全部权限信息
class GroupDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'name','permissions')

#用户基本信息
class UserCommenSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ('id', 'nameC','nameE','org','photoKey','tags','title','gender')

#用户全部信息
class UserSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(MyUser.groups,many=True)
    class Meta:
        model = MyUser
        fields = '__all__'
        read_only_fields = ('datasource', 'usercode')
        depth = 1

#创建用户所需信息
class CreatUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        # fields = ('groups','photoBucket','photoKey','cardBucket','cardKey','wechat','org','name','nameE','mobileAreaCode','mobile','description','tags','email','title','gender','school','specialty','registersource','remark',)
        exclude = ('password','datasource')

# 用户列表显示信息
class UserListSerializer(serializers.ModelSerializer):
    groups = GroupDetailSerializer(MyUser.groups,many=True)
    org = OrgCommonSerializer(MyUser.org)
    investor_relations = UserRelationSerializer(MyUser.investor_relations, many=True)
    class Meta:
        model = MyUser
        fields = ('id','groups','tags','nameC','nameE','mobile','email','title','org','investor_relations')
        depth = 1


