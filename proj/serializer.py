from rest_framework import serializers

from proj.models import project, finance, favorite
from usersys.serializer import UserSerializer

class FinanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = finance
        fields = '__all__'
        # fields = ('id','incomeFrom','incomeTo')


class FormatSerializer(serializers.ModelSerializer):
    class Meta:
        model = finance
        fields = '__all__'
        # fields = ('id','incomeFrom','incomeTo')


class ProjSerializer(serializers.ModelSerializer):
    supportUser = UserSerializer(project.supportUser)
    proj_finance= FinanceSerializer(many=True)
    class Meta:
        model = project
        # fields = '__all__'
        fields = ('id','supportUser','projFormat','proj_finance')
        depth = 1


class FavoriteSerializer(serializers.ModelSerializer):
    user = UserSerializer(favorite.user)
    proj = ProjSerializer(favorite.proj)
    class Meta:
        model = favorite
        fields = '__all__'
        # fields = ('id','proj','user','favoritetype')
        depth = 1

class ProjCreatSerializer(serializers.ModelSerializer):
    class Meta:
        model = project
        fields = ('titleC','statu','currency','projFormat','tags')