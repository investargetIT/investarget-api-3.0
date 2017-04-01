from rest_framework import serializers

from timeline.models import timeline,timelineremark,timelineTransationStatu


class TimeLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = timeline
        fields = ('id', 'proj', 'investor','supporter','trader','isClose','closeDate')

class TimeLineRemarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = timelineremark
        fields = '__all__'

class TimeLineStatuSerializer(serializers.ModelSerializer):
    class Meta:
        model = timelineTransationStatu
        fields = '__all__'