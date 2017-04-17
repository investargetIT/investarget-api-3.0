from rest_framework import serializers

from org.models import organization


class OrgCommonSerializer(serializers.ModelSerializer):
    class Meta:
        model = organization
        fields = ('id','name','auditStatu')

class OrgSerializer(serializers.ModelSerializer):
    class Meta:
        model = organization
        exclude = ('id','name','orgcode','auditStatu',)

class OrgDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = organization
        fileds = '__all__'

class CreateOrgSerializer(serializers.ModelSerializer):
    class Meta:
        model = organization
        fields = '__all__'