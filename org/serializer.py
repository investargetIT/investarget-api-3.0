
from rest_framework import serializers
from org.models import organization, orgRemarks, orgTransactionPhase, orgBuyout, orgContact, orgInvestEvent, \
    orgCooperativeRelationship, orgManageFund
from sourcetype.serializer import transactionPhasesSerializer, orgAreaSerializer


class OrgCommonSerializer(serializers.ModelSerializer):
    class Meta:
        model = organization
        fields = ('id', 'orgfullname', 'orgnameC', 'orgnameE', 'description')


class OrgCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = organization
        fields = '__all__'


class OrgUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = organization
        exclude = ('datasource', 'createuser', 'createdtime')


class OrgTransactionPhaseSerializer(serializers.ModelSerializer):
    transactionPhase = serializers.StringRelatedField()
    class Meta:
        model = orgTransactionPhase
        fields = ('transactionPhase', 'is_deleted')


class OrgDetailSerializer(serializers.ModelSerializer):
    orgtransactionphase = serializers.SerializerMethodField()

    class Meta:
        model = organization
        depth = 1
        exclude = ('datasource', 'createuser', 'createdtime', 'is_deleted', 'deleteduser', 'deletedtime', 'lastmodifyuser', 'lastmodifytime',)

    def get_orgtransactionphase(self, obj):
        usertrader = obj.orgtransactionphase.filter(transactionPhase_orgs__is_deleted=False)
        if usertrader.exists():
            return transactionPhasesSerializer(usertrader, many=True).data
        return None


class OrgRemarkDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = orgRemarks
        fields = '__all__'


class OrgBuyoutCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = orgBuyout
        fields = '__all__'


class OrgBuyoutSerializer(serializers.ModelSerializer):

    class Meta:
        model = orgBuyout
        exclude = ('createuser', 'deleteduser', 'createdtime', 'is_deleted', 'deletedtime', 'lastmodifytime')


class OrgContactCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = orgContact
        fields = '__all__'


class OrgContactSerializer(serializers.ModelSerializer):

    class Meta:
        model = orgContact
        exclude = ('createuser', 'deleteduser', 'createdtime', 'is_deleted', 'deletedtime', 'lastmodifytime')


class OrgInvestEventCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = orgInvestEvent
        fields = '__all__'


class OrgInvestEventSerializer(serializers.ModelSerializer):

    class Meta:
        model = orgInvestEvent
        exclude = ('createuser', 'deleteduser', 'createdtime', 'is_deleted', 'deletedtime', 'lastmodifytime')


class OrgCooperativeRelationshipCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = orgCooperativeRelationship
        fields = '__all__'


class OrgCooperativeRelationshipSerializer(serializers.ModelSerializer):

    class Meta:
        model = orgCooperativeRelationship
        exclude = ('createuser', 'deleteduser', 'createdtime', 'is_deleted', 'deletedtime', 'lastmodifytime')


class OrgManageFundCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = orgManageFund
        fields = '__all__'


class OrgManageFundSerializer(serializers.ModelSerializer):

    class Meta:
        model = orgManageFund
        exclude = ('createuser', 'deleteduser', 'createdtime', 'is_deleted', 'deletedtime', 'lastmodifytime')