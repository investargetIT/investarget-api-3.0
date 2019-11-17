from rest_framework import serializers

from dataroom.models import dataroom, dataroomdirectoryorfile, dataroom_User_file, dataroom_User_template
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

class DataroomdirectoryorfilePathSerializer(serializers.ModelSerializer):
    fileurl = serializers.SerializerMethodField()
    filepath = serializers.SerializerMethodField()
    class Meta:
        model = dataroomdirectoryorfile
        exclude = ('is_deleted', 'deleteduser', 'deletedtime', 'lastmodifyuser', 'lastmodifytime',)

    def get_fileurl(self, obj):
        if obj.bucket and obj.key:
            return getUrlWithBucketAndKey(obj.bucket, obj.key)
        else:
            return None

    def get_filepath(self, obj):
        if obj.parent:
            return self.get_filepath(obj.parent) + '/' + obj.filename
        else:
            return obj.filename

class User_DataroomfileCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = dataroom_User_file
        fields = '__all__'

class User_DataroomSerializer(serializers.ModelSerializer):
    dataroom = DataroomSerializer()
    user = UserInfoSerializer()
    trader = UserInfoSerializer()
    class Meta:
        model = dataroom_User_file
        fields = ('id', 'dataroom', 'user', 'trader')

class User_DataroomfileSerializer(serializers.ModelSerializer):
    files = DataroomdirectoryorfileSerializer(many=True)
    class Meta:
        model = dataroom_User_file
        fields = ('id', 'dataroom', 'user', 'files', 'trader')

class User_DataroomfileFileIdsSerializer(serializers.ModelSerializer):
    class Meta:
        model = dataroom_User_file
        fields = ('id', 'dataroom', 'user', 'files')

class User_DataroomTemplateCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = dataroom_User_template
        fields = '__all__'

class User_DataroomTemplateSerializer(serializers.ModelSerializer):
    dataroomUserfile = User_DataroomfileFileIdsSerializer()

    class Meta:
        model = dataroom_User_template
        fields = ('id', 'dataroom', 'user', 'dataroomUserfile')

