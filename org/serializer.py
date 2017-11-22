
from rest_framework import serializers
from org.models import organization, orgRemarks, orgTransactionPhase
from sourcetype.serializer import transactionPhasesSerializer


class OrgCommonSerializer(serializers.ModelSerializer):
    class Meta:
        model = organization
        fields = ('id','orgnameC','orgnameE','description')

class OrgCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = organization
        fields = '__all__'

class OrgUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = organization
        exclude = ('datasource','createuser','createdtime')


class OrgTransactionPhaseSerializer(serializers.ModelSerializer):
    transactionPhase = serializers.StringRelatedField()
    class Meta:
        model = orgTransactionPhase
        fields = ('transactionPhase','is_deleted')

class OrgDetailSerializer(serializers.ModelSerializer):
    orgtransactionphase = serializers.SerializerMethodField()

    class Meta:
        model = organization
        depth = 1
        exclude = ('datasource', 'createuser', 'createdtime','is_deleted','deleteduser','deletedtime','lastmodifyuser','lastmodifytime',)

    def get_orgtransactionphase(self, obj):
        usertrader = obj.orgtransactionphase.filter(transactionPhase_orgs__is_deleted=False)
        if usertrader.exists():
            return transactionPhasesSerializer(usertrader,many=True).data
        return None

class OrgRemarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = orgRemarks
        fields = ('id','org','remark','createdtime')

class OrgRemarkDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = orgRemarks
        fields = '__all__'