from rest_framework import serializers

from emailmanage.models import emailgroupsendlist
from sourcetype.models import Tag, Industry, Country, TransactionType
from usersys.models import MyUser


class Usergroupsendlistserializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ('id', 'usernameC', 'email')

class Industrygroupsendlistserializer(serializers.ModelSerializer):
    class Meta:
        model = Industry
        fields = ('industryC',)

class TransactionTypegroupsendlistserializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionType
        fields = ('nameC',)

class Taggroupsendlistserializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('nameC',)


class Emailgroupsendlistserializer(serializers.ModelSerializer):
    class Meta:
        model = emailgroupsendlist
        exclude = ('is_deleted',)