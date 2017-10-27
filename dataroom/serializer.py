from rest_framework import serializers

from dataroom.models import dataroom, dataroomdirectoryorfile, dataroom_User_file
from proj.serializer import ProjCommonSerializer
from third.views.qiniufile import getUrlWithBucketAndKey
from usersys.serializer import UserInfoSerializer


class DataroomCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = dataroom
        fields = '__all__'


class DataroomSerializer(serializers.ModelSerializer):
    proj = ProjCommonSerializer()
    class Meta:
        model = dataroom
        exclude = ('is_deleted', 'deleteduser', 'deletedtime', 'lastmodifyuser', 'lastmodifytime',)

class DataroomdirectoryorfileCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = dataroomdirectoryorfile
        fields = '__all__'

class DataroomdirectoryorfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = dataroomdirectoryorfile
        fields = '__all__'
        read_only_fields = ('datasource','createuser','createtime','isFile','dataroom','key')

class DataroomdirectoryorfileSerializer(serializers.ModelSerializer):
    fileurl = serializers.SerializerMethodField()
    class Meta:
        model = dataroomdirectoryorfile
        exclude = ('is_deleted', 'deleteduser', 'deletedtime', 'lastmodifyuser', 'lastmodifytime',)

    def get_fileurl(self, obj):
        if obj.bucket and obj.key:
            return getUrlWithBucketAndKey(obj.bucket, obj.key)
        else:
            return None

class User_DataroomfileCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = dataroom_User_file
        fields = '__all__'

class User_DataroomSerializer(serializers.ModelSerializer):
    dataroom = DataroomSerializer()
    class Meta:
        model = dataroom_User_file
        fields = ('dataroom', 'user')

class User_DataroomfileSerializer(serializers.ModelSerializer):
    files = DataroomdirectoryorfileSerializer()
    class Meta:
        model = dataroom_User_file
        fields = ('dataroom', 'user', 'files')