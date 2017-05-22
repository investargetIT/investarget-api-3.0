from rest_framework import serializers

from sourcetype.models import TransactionType, TransactionPhases, Specialty, School, OrgArea, Tag, Industry, CurrencyType, \
    AuditStatus, ProjectStatus, OrgType, FavoriteType, MessageType, ClientType, TitleType, Continent, Country, \
    DataSource, TransactionStatus


class AuditStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditStatus
        fields = '__all__'

class projectStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectStatus
        fields = '__all__'

class orgTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrgType
        fields = '__all__'

class favoriteTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteType
        fields = '__all__'

class messageTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageType
        fields = '__all__'


class clientTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientType
        fields = '__all__'


class titleTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TitleType
        fields = '__all__'


class continentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Continent
        fields = '__all__'


class countrySerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    class Meta:
        model = Country
        fields = '__all__'
    def get_url(self, obj):
        if not obj.key:
            return 'https://o79atf82v.qnssl.com/' + '040.jpg'
        return 'https://o79atf82v.qnssl.com/' + obj.key


class currencyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurrencyType
        fields = '__all__'


class industrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Industry
        fields = '__all__'


class tagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class orgAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrgArea
        fields = '__all__'


class schoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = '__all__'


class professionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialty
        fields = '__all__'


class transactionPhasesSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionPhases
        fields = '__all__'

class transactionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionType
        fields = '__all__'

class transactionStatuSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionStatus
        fields = '__all__'


class DataSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataSource
        fields = ('id',)