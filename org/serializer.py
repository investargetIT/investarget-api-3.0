from rest_framework import serializers

from org.models import organization, orgRemarks


# from usersys.serializer import UserCommenSerializer
from sourcetype.serializer import transactionPhasesSerializer


class OrgCommonSerializer(serializers.ModelSerializer):
    # org_users = UserCommenSerializer(many=True)
    class Meta:
        model = organization
        fields = ('id','nameC','nameE',)

class OrgSerializer(serializers.ModelSerializer):
    class Meta:
        model = organization
        fileds = ('id','nameC','nameE','orgcode','orgstatus','org_users')

class OrgDetailSerializer(serializers.ModelSerializer):
    transactionPhases = transactionPhasesSerializer(source='get_transactionPhases', many=True)
    class Meta:
        model = organization
        # exclude = ('id',)
        fields = '__all__'


class OrgRemarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = orgRemarks
        fields = ('id','org','remark','createtime')

class OrgRemarkDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = orgRemarks
        fields = '__all__'