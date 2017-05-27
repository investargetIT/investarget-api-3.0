from collections import OrderedDict

from django.db.models import Manager
from django.db.models import QuerySet
from django.db.models.query import Prefetch
from rest_framework import serializers
from rest_framework.fields import SkipField, get_attribute, is_simple_callable
from rest_framework.relations import PKOnlyObject

from org.models import organization, orgRemarks, orgTransactionPhase

# from usersys.serializer import UserCommenSerializer
from sourcetype.serializer import transactionPhasesSerializer


class OrgCommonSerializer(serializers.ModelSerializer):
    # org_users = UserCommenSerializer(many=True)
    class Meta:
        model = organization
        fields = ('id','orgnameC','orgnameE',)

class OrgSerializer(serializers.ModelSerializer):

    class Meta:
        model = organization
        fields = ('id','orgnameC','orgnameE','orgcode','orgstatus','org_users')



class OrgCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = organization
        fields = '__all__'

class OrgTransactionPhaseSerializer(serializers.ModelSerializer):
    transactionPhase = serializers.StringRelatedField()
    class Meta:
        model = orgTransactionPhase
        fields = ('transactionPhase','is_deleted')

class OrgDetailSerializer(serializers.ModelSerializer):
    # orgtransactionphase = serializers.SerializerMethodField()
    # orgtransactionphase = OrgTransactionPhaseSerializer(source='org_orgTransactionPhases',many=True)


    class Meta:
        model = organization
        fields = ('id','orgnameC','orgnameE','industry','currency','decisionCycle','orgcode','orgtransactionphase','orgtype')
        depth = 1

    # def get_orgtransactionphase(self, obj):
    #     usertrader = obj.orgtransactionphase.filter(transactionPhase_orgs__is_deleted=False)
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