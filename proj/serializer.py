from rest_framework import serializers

from proj.models import project, finance, favoriteProject, attachment
from usersys.serializer import UserCommenSerializer


class FinanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = finance
        fields = '__all__'
        # exclude = ('id','proj','deleteduser','deletedtime','createuser','createdtime','lastmodifyuser','lastmodifytime','is_deleted')

class FinanceChangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = finance
        fields = '__all__'
        # read_only_fields = ('datasource','createuser','createdtime','proj')

class FinanceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = finance
        fields = '__all__'
        # read_only_fields = ('deletedtime', 'lastmodifyuser', 'lastmodifytime', 'is_deleted', 'deleteduser')


class ProjFinanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = finance
        exclude = ('deleteduser','deletedtime','createuser','createdtime','lastmodifyuser','lastmodifytime',)



class ProjAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = attachment
        exclude = ('deleteduser', 'deletedtime', 'createuser', 'createdtime', 'lastmodifyuser', 'lastmodifytime',)


class ProjSerializer(serializers.ModelSerializer):
    supportUser = UserCommenSerializer(project.supportUser)
    proj_finances = ProjFinanceSerializer(many=True)
    proj_attachment = ProjAttachmentSerializer(many=True)
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

#list
class ProjListSerializer_admin(serializers.ModelSerializer):
    finance = serializers.SerializerMethodField()
    attachment = serializers.SerializerMethodField()

    class Meta:
        model = project
        fields = ('id','industries','projtitleC','projtitleE','tags','financeAmount','financeAmount_USD','country','projstatus','isHidden','finance')
        depth = 1

    def get_finance(self, obj):
        usertrader = obj.proj_finances.filter(is_deleted=False)
        if usertrader.exists():
            return FinanceSerializer(usertrader,many=True).data
        return None

    def get_attactment(self, obj):
        usertrader = obj.proj_attachment.filter(is_deleted=False)
        if usertrader.exists():
            return ProjAttachmentSerializer(usertrader, many=True).data
        return None

class ProjListSerializer_user(serializers.ModelSerializer):
    class Meta:
        model = project
        fields = ('id', 'projtitleC', 'projtitleE')
#detail
class ProjDetailSerializer_admin_withsecretinfo(serializers.ModelSerializer):
    finance = serializers.SerializerMethodField()
    attachment = serializers.SerializerMethodField()

    class Meta:
        model = project
        fields = '__all__'
        depth = 1

    def get_finance(self, obj):
        usertrader = obj.proj_finances.filter(is_deleted=False)
        if usertrader.exists():
            return FinanceSerializer(usertrader, many=True).data
        return None

    def get_attactment(self, obj):
        usertrader = obj.proj_attachment.filter(is_deleted=False)
        if usertrader.exists():
            return ProjAttachmentSerializer(usertrader, many=True).data
        return None
class UserDetailSerializer_user_withsecretinfo(serializers.ModelSerializer):
    finance = serializers.SerializerMethodField()
    attachment = serializers.SerializerMethodField()

    class Meta:
        model = project
        fields = '__all__'
        depth = 1

    def get_finance(self, obj):
        usertrader = obj.proj_finances.filter(is_deleted=False)
        if usertrader.exists():
            return FinanceSerializer(usertrader, many=True).data
        return None

    def get_attactment(self, obj):
        usertrader = obj.proj_attachment.filter(is_deleted=False)
        if usertrader.exists():
            return ProjAttachmentSerializer(usertrader, many=True).data
        return None


class ProjDetailSerializer_admin_withoutsecretinfo(serializers.ModelSerializer):
    finance = serializers.SerializerMethodField()
    attachment = serializers.SerializerMethodField()

    class Meta:
        model = project
        fields = (
        'id', 'industries', 'projtitleC', 'projtitleE', 'tags', 'financeAmount', 'financeAmount_USD', 'country',
        'projstatus', 'isHidden', 'finance')
        depth = 1

    def get_finance(self, obj):
        usertrader = obj.proj_finances.filter(is_deleted=False)
        if usertrader.exists():
            return FinanceSerializer(usertrader, many=True).data
        return None

    def get_attactment(self, obj):
        usertrader = obj.proj_attachment.filter(is_deleted=False)
        if usertrader.exists():
            return ProjAttachmentSerializer(usertrader, many=True).data
        return None
class ProjDetailSerializer_user_withoutsecretinfo(serializers.ModelSerializer):
    finance = serializers.SerializerMethodField()
    attachment = serializers.SerializerMethodField()

    class Meta:
        model = project
        fields = (
        'id', 'industries', 'projtitleC', 'projtitleE', 'tags', 'financeAmount', 'financeAmount_USD', 'country',
        'projstatus', 'isHidden', 'finance')
        depth = 1

    def get_finance(self, obj):
        usertrader = obj.proj_finances.filter(is_deleted=False)
        if usertrader.exists():
            return FinanceSerializer(usertrader, many=True).data
        return None

    def get_attactment(self, obj):
        usertrader = obj.proj_attachment.filter(is_deleted=False)
        if usertrader.exists():
            return ProjAttachmentSerializer(usertrader, many=True).data
        return None