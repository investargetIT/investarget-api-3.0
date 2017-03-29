from rest_framework import serializers

from types.models import auditStatus, projectStatus, orgType, favoriteType, messageType, clientType, titleType, \
    continent, country, currencyType, industry, tag, orgArea, school, profession, transactionPhases, transactionType


class AuditStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = auditStatus
        fields = '__all__'

class projectStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = projectStatus
        fields = '__all__'

class orgTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = orgType
        fields = '__all__'

class favoriteTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = favoriteType
        fields = '__all__'

class messageTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = messageType
        fields = '__all__'


class clientTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = clientType
        fields = '__all__'


class titleTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = titleType
        fields = '__all__'


class continentSerializer(serializers.ModelSerializer):
    class Meta:
        model = continent
        fields = '__all__'


class countrySerializer(serializers.ModelSerializer):
    class Meta:
        model = country
        fields = '__all__'


class currencyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = currencyType
        fields = '__all__'


class industrySerializer(serializers.ModelSerializer):
    class Meta:
        model = industry
        fields = '__all__'


class tagSerializer(serializers.ModelSerializer):
    class Meta:
        model = tag
        fields = '__all__'


class orgAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = orgArea
        fields = '__all__'


class schoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = school
        fields = '__all__'


class professionSerializer(serializers.ModelSerializer):
    class Meta:
        model = profession
        fields = '__all__'


class transactionPhasesSerializer(serializers.ModelSerializer):
    class Meta:
        model = transactionPhases
        fields = '__all__'

class transactionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = transactionType
        fields = '__all__'