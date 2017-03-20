from rest_framework import serializers

from proj.models import project, finance, favorite
from MyUserSys.serializer import UserSerializer


class ProjSerializer(serializers.ModelSerializer):
    supportuser = UserSerializer(project.supportuser)
    class Meta:
        model = project
        # fields = '__all__'
        fields = ('id','title','statu','supportuser','description','finance')
        depth = 1

class FinanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = finance
        fields = ('id','incomeFrom','incomeTo')

class FavoriteSerializer(serializers.ModelSerializer):
    user = UserSerializer(favorite.user)
    proj = ProjSerializer(favorite.proj)
    class Meta:
        model = favorite
        fields = ('id','proj','user','favoritetype')
        depth = 1