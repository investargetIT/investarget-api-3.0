from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from msg.models import message, schedule, webexUser
from proj.serializer import ProjCommonSerializer
from sourcetype.serializer import countrySerializer, orgAreaSerializer
from usersys.serializer import UserCommenSerializer,UserInfoSerializer


class ScheduleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = schedule
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset = schedule.objects.filter(type=4, is_deleted=False),
                fields = ('type', 'scheduledtime')
            )
        ]

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


class WebEXUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = webexUser
        fields = '__all__'