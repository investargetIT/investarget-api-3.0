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
        fields = ('id','nameC','nameE','orgcode','orgstatus','org_users')

class OrgDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = organization
        fields = '__all__'

    # def get_transactionPhases(self, obj):
    #     usertrader = obj.orgtransactionphase
    #     if usertrader.exists():
    #         return transactionPhasesSerializer(usertrader,many=True).data
    #     return None
class OrgRemarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = orgRemarks
        fields = ('id','org','remark','createtime')

class OrgRemarkDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = orgRemarks
        fields = '__all__'