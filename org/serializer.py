from rest_framework import serializers

from org.models import organization


class OrgSerializer(serializers.ModelSerializer):
    class Meta:
        model = organization
        # fields = '__all__'
        fields = ('id','name','orgcode','orgstatu','orgdescription')
        depth = 1