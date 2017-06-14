from rest_framework import serializers

from proj.models import project, finance, favoriteProject, attachment
from usersys.serializer import UserCommenSerializer


class FinanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = finance
        fields = '__all__'
        # exclude = ('id','proj','deleteuser','deletetime','createuser','createtime','lastmodifyuser','lastmodifytime','is_deleted')

class FinanceChangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = finance
        fields = '__all__'
        read_only_fields = ('datasource','createuser','createtime','proj')

class FinanceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = finance
        fields = '__all__'
        read_only_fields = ('deletetime', 'lastmodifyuser', 'lastmodifytime', 'is_deleted', 'deleteuser')


class ProjFinanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = finance
        exclude = ('deleteuser','deletetime','createuser','createtime','lastmodifyuser','lastmodifytime',)



class ProjAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = attachment
        fileds = '__all__'


class ProjSerializer(serializers.ModelSerializer):
    supportUser = UserCommenSerializer(project.supportUser)
    proj_finances = ProjFinanceSerializer(many=True)
    class Meta:
        model = project
        fields = '__all__'
        depth = 1

class ProjCommonSerializer(serializers.ModelSerializer):
    class Meta:
        model = project
        fields = ('id','industries','projtitleC','projtitleE','tags','financeAmount','financeAmount_USD','country','projstatus','isHidden')
        depth = 1

class ProjCreatSerializer(serializers.ModelSerializer):
    class Meta:
        model = project
        fields = '__all__'




class FavoriteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = favoriteProject
        fields = '__all__'


class FavoriteSerializer(serializers.ModelSerializer):
    user = UserCommenSerializer()
    proj = ProjCommonSerializer()
    class Meta:
        model = favoriteProject
        fields = '__all__'
        # fields = ('id','proj','user','trader','favoritetype')
        # depth = 1

