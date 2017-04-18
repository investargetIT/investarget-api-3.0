from rest_framework import serializers

from proj.models import project, finance, favorite
from usersys.serializer import UserSerializer

class FinanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = finance
        # fields = '__all__'
        exclude = ('id','proj','deleteuser','deletetime','createuser','createtime','lastmodifyuser','lastmodifytime','is_deleted')


class FormatSerializer(serializers.ModelSerializer):
    class Meta:
        model = finance
        fields = '__all__'
        # fields = ('id','incomeFrom','incomeTo')


class ProjSerializer(serializers.ModelSerializer):
    supportUser = UserSerializer(project.supportUser)
    proj_finances = FinanceSerializer(many=True)
    class Meta:
        model = project
        fields = '__all__'
        depth = 1

class ProjCommonSerializer(serializers.ModelSerializer):
    class Meta:
        model = project
        fields = ('id','industries','titleC','tags','financeAmount','financeAmount_USD','country','statu','isHidden')
        depth = 1

class ProjCreatSerializer(serializers.ModelSerializer):
    class Meta:
        model = project
        fields = '__all__'







class FavoriteSerializer(serializers.ModelSerializer):
    user = UserSerializer(favorite.user)
    proj = ProjSerializer(favorite.proj)
    class Meta:
        model = favorite
        fields = '__all__'
        # fields = ('id','proj','user','favoritetype')
        depth = 1

