from django.contrib.auth.models import Group
from rest_framework import serializers

from .models import MyUser, UserRelation, userTags

class UserRelationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRelation
        fields = ('investoruser','traderuser','relationtype')

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id','name',)

class UserCommenSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ('id', 'groups', 'name',)


class UserSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(MyUser.groups,many=True)
    investor_relations = UserRelationSerializer(MyUser.investor_relations,many=True)
    class Meta:
        model = MyUser
        # fields = '__all__'
        fields = ('id','groups','name','is_superuser','userstatu','investor_relations')
        depth = 1

class CreatUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ('groups','name','userstatu','trader')


class UserListSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(MyUser.groups,many=True)
    investor_relations = UserRelationSerializer(MyUser.investor_relations, many=True)
    class Meta:
        model = MyUser
        # fields = '__all__'
        fields = ('id','groups','name','is_superuser','userstatu','investor_relations')
        depth = 1

class UserTagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = userTags
        fields = '__all__'



