from rest_framework import serializers

from msg.models import message, schedule
from proj.serializer import ProjCommonSerializer
from sourcetype.serializer import countrySerializer, orgAreaSerializer
from usersys.serializer import UserCommenSerializer,UserInfoSerializer


class ScheduleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = schedule
        fields = '__all__'

class ScheduleSerializer(serializers.ModelSerializer):
    user = UserInfoSerializer()
    createuser = UserCommenSerializer()
    country = countrySerializer()
    proj = ProjCommonSerializer()
    location = orgAreaSerializer()

    class Meta:
        model = schedule
        exclude = ('deleteduser', 'datasource', 'is_deleted', 'deletedtime', 'lastmodifytime')


class MsgSerializer(serializers.ModelSerializer):
    class Meta:
        model = message
        fields = '__all__'