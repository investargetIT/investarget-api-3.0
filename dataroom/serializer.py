from rest_framework import serializers

from dataroom.models import dataroom, dataroomdirectoryorfile
from proj.serializer import ProjCommonSerializer
from third.views.qiniufile import getUrlWithBucketAndKey
from usersys.serializer import UserInfoSerializer


class DataroomCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = dataroom
        fields = '__all__'


class DataroomSerializer(serializers.ModelSerializer):
    proj = ProjCommonSerializer()
    trader = UserInfoSerializer()
    investor = UserInfoSerializer()
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
        read_only_fields = ('datasource','createuser','createtime','isFile','isShadow','shadowdirectory','dataroom')

class DataroomdirectoryorfileSerializer(serializers.ModelSerializer):
    fileurl = serializers.SerializerMethodField()
    class Meta:
        model = dataroomdirectoryorfile
        fields = '__all__'

    def get_fileurl(self, obj):
        if obj.bucket and obj.key:
            return getUrlWithBucketAndKey(obj.bucket, obj.key)
        else:
            return None