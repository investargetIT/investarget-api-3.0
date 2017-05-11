from rest_framework import serializers

from msg.models import message


class MsgSerializer(serializers.ModelSerializer):
    class Meta:
        model = message
        # fields = ('id','content','type','title','receiver','isread','created','sender')
        fields = '__all__'
        # depth = 1