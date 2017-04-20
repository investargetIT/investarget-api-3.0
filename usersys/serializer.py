#coding=utf-8
from django.contrib.auth.models import Group
from django.db.models.fields.reverse_related import ForeignObjectRel
from rest_framework import serializers

from org.serializer import OrgCommonSerializer
from .models import MyUser, UserRelation, userTags

#用户关系基本信息
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
        read_only_fields = ('datasource', 'usercode')
        depth = 1

#创建用户所需信息
class CreatUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        # fields = ('groups','photoBucket','photoKey','cardBucket','cardKey','wechat','org','name','nameE','mobileAreaCode','mobile','company','description','tags','email','title','gender','school','specialty','registersource','remark',)
        exclude = ('password','datasource')

# 用户列表显示信息
class UserListSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(MyUser.groups,many=True)
    org = OrgCommonSerializer(MyUser.org)
    investor_relations = UserRelationSerializer(MyUser.investor_relations, many=True)
    class Meta:
        model = MyUser
        fields = ('id','groups','tags','name','mobile','email','title','company','org','investor_relations')
        depth = 1




def dictToLang(dictdata,lang=None):
    newdict = {}
    if lang == 'en':
        for key,value in dictdata.items():
            if key[-1] == 'E' and dictdata.has_key(key[0:-1]+'C'):
                newdict[key[0:-1]] = value
            elif key[-1] == 'C' and dictdata.has_key(key[0:-1]+'E'):
                pass
            else:
                if isinstance(value,dict):
                    minvaluedict = {}
                    for minkey, minvalue in value.items():
                        print minkey[-1], minkey[0:-1] + 'E'
                        if minkey[-1] == 'E' and value.has_key(minkey[0:-1] + 'C'):
                            minvaluedict[minkey[0:-1]] = minvalue
                        elif minkey[-1] == 'C' and value.has_key(minkey[0:-1] + 'E'):
                            pass
                        else:

                            minvaluedict[minkey] = minvalue
                    newdict[key] = minvaluedict
                elif isinstance(value,list):
                    newlist = []
                    for minvalues in value:
                        if isinstance(minvalues, dict):
                            minxvalue = {}
                            for minikey, minivalue in minvalues.items():
                                if minikey[-1] == 'E' and minvalues.has_key(minikey[0:-1] + 'C'):
                                    minxvalue[minikey[0:-1]] = minivalue
                                elif minikey[-1] == 'C' and minvalues.has_key(minikey[0:-1] + 'E'):
                                    pass
                                else:
                                    minxvalue[minikey] = minivalue
                            newlist.append(minxvalue)
                        else:
                            newlist.append(minvalues)
                    newdict[key] = newlist
                else:
                    newdict[key] = value
    else:
        for key,value in dictdata.items():
            if key[-1] == 'E' and dictdata.has_key(key[0:-1]+'C'):
                pass
            elif key[-1] == 'C' and dictdata.has_key(key[0:-1]+'E'):
                newdict[key[0:-1]] = value
            else:
                if isinstance(value,dict):
                    minvaluedic = {}
                    for minkey, minvalue in value.items():
                        if minkey[-1] == 'E' and value.has_key(minkey[0:-1] + 'C'):
                            pass
                        elif minkey[-1] == 'C' and value.has_key(minkey[0:-1] + 'E'):
                            minvaluedic[minkey[0:-1]] = minvalue
                        else:
                            minvaluedic[minkey] = minvalue
                    newdict[key] = minvaluedic
                elif isinstance(value,list):
                    newlist = []
                    for minvalues in value:
                        if isinstance(minvalues, dict):
                            minxvalue = {}
                            for minikey, minivalue in minvalues.items():
                                if minikey[-1] == 'E' and minvalues.has_key(minikey[0:-1] + 'C'):
                                    pass
                                elif minikey[-1] == 'C' and minvalues.has_key(minikey[0:-1] + 'E'):
                                    minxvalue[minikey[0:-1]] = minivalue
                                else:
                                    minxvalue[minikey] = minivalue
                            newlist.append(minxvalue)
                        else:
                            newlist.append(minvalues)
                    newdict[key] = newlist
                else:
                    newdict[key] = value

    return newdict