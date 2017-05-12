from rest_framework import serializers

from sourcetype.serializer import transactionStatuSerializer
from timeline.models import timeline,timelineremark,timelineTransationStatu


class TimeLineStatuCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = timelineTransationStatu
        fields = '__all__'

class TimeLineStatuSerializer(serializers.ModelSerializer):
    transationStatus = transactionStatuSerializer()
    class Meta:
        model = timelineTransationStatu
        fields = ('transationStatus','timeline','isActive','id')

class TimeLineSerializer(serializers.ModelSerializer):
    transationStatu = TimeLineStatuSerializer(source='get_timelinestatus',many=True)
    class Meta:
        model = timeline
        fields = ('id', 'proj', 'investor','supportor','trader','isClose','closeDate','transationStatu')

class TimeLineHeaderListSerializer(serializers.ModelSerializer):
    transationStatu = TimeLineStatuSerializer(source='get_timelinestatus',many=True)
    class Meta:
        model = timeline
        fields = ('id', 'proj', 'investor','transationStatu')



class TimeLineCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = timeline
        # fields = '__all__'
        exclude = ('is_deleted','deleteduser','deletedtime','lastmodifyuser','lastmodifytime')

class TimeLineRemarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = timelineremark
        fields = '__all__'
