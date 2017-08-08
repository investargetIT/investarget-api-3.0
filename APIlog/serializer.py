from rest_framework import serializers

from APIlog.models import APILog, loginlog,userviewprojlog


class APILogSerializer(serializers.ModelSerializer):
    class Meta:
        model = APILog
        exclude = ('is_deleted', 'datasource')

class LoginLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = loginlog
        exclude = ('is_deleted', 'datasource')

class ViewProjLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = userviewprojlog
        exclude = ('is_deleted', 'datasource')