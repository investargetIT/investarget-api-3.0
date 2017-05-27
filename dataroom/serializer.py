from rest_framework import serializers

from dataroom.models import dataroom, dataroomdirectoryorfile


class DataroomCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = dataroom
        fields = '__all__'

class DataroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = dataroom
        fields = '__all__'

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
    class Meta:
        model = dataroomdirectoryorfile
        fields = '__all__'