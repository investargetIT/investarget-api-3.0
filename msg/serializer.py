from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from msg.models import message, schedule, webexUser, webexMeeting
from proj.serializer import ProjCommonSerializer
from sourcetype.serializer import countrySerializer, orgAreaSerializer
from third.thirdconfig import webEX_webExID, webEX_password
from usersys.serializer import UserCommenSerializer,UserInfoSerializer

class MsgSerializer(serializers.ModelSerializer):
    class Meta:
        model = message
        fields = '__all__'


class WebEXMeetingSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    class Meta:
        model = webexMeeting
        exclude = ('deleteduser', 'datasource', 'is_deleted', 'deletedtime')

    def get_url(self, objc):
        return 'https://investarget.webex.com.cn/investarget/p.php?AT=LI&WID={}&PW={}'.format(webEX_webExID, webEX_password)


class ScheduleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = schedule
        fields = '__all__'

class ScheduleMeetingSerializer(serializers.ModelSerializer):
    meeting = WebEXMeetingSerializer()
    class Meta:
        model = schedule
        exclude = ('deleteduser', 'datasource', 'is_deleted', 'deletedtime')


class ScheduleSerializer(serializers.ModelSerializer):
    user = UserInfoSerializer()
    createuser = UserCommenSerializer()
    country = countrySerializer()
    proj = ProjCommonSerializer()
    location = orgAreaSerializer()
    meeting = WebEXMeetingSerializer()
    class Meta:
        model = schedule
        exclude = ('deleteduser', 'datasource', 'is_deleted', 'deletedtime')


class WebEXUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = webexUser
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=webexUser.objects.filter(is_deleted=False),
                fields=('meeting', 'email')
            )
        ]