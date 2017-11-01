from rest_framework import serializers

from msg.models import message, schedule
from usersys.serializer import UserCommenSerializer


class ScheduleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = schedule
        fields = '__all__'

class ScheduleSerializer(serializers.ModelSerializer):
    user = UserCommenSerializer()
    createuser = UserCommenSerializer()
    class Meta:
        model = schedule
        fields = ('id','comments','scheduledtime','user','address','projtitle','proj','createuser','createdtime')



class MsgSerializer(serializers.ModelSerializer):
    class Meta:
        model = message
        # fields = ('id','content','type','messagetitle','receiver','isread','created','sender')
        fields = '__all__'
        # depth = 1