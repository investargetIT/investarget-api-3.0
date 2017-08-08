from rest_framework import serializers

from proj.models import project, finance, favoriteProject, attachment, projServices, projectIndustries
from sourcetype.serializer import tagSerializer, transactionTypeSerializer, serviceSerializer
from third.views.qiniufile import getUrlWithBucketAndKey
from usersys.serializer import UserCommenSerializer

class ProjSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = project
        fields = ('id','projtitleC','projtitleE','financeAmount','financeAmount_USD','country','projstatus','isHidden','ismarketplace')


class ProjIndustrySerializer(serializers.ModelSerializer):
    nameC = serializers.CharField(source='projectIndustries.industry__industryC', read_only=True)
    nameE = serializers.CharField(source='projectIndustries.industry__industryE', read_only=True)
    url = serializers.SerializerMethodField()
    class Meta:
        model = projectIndustries
        fields = ('industry','bucket','key','url','nameC','nameE')
    def get_url(self, obj):
        if obj.key:
            return 'https://o79atf82v.qnssl.com/' + obj.key
        return None

class ProjIndustryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = projectIndustries
        fields = '__all__'

class FinanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = finance
        fields = '__all__'
        # exclude = ('id','proj','deleteduser','deletedtime','createuser','createdtime','lastmodifyuser','lastmodifytime','is_deleted')

class FinanceChangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = finance
        exclude = ('datasource',)

class FinanceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = finance
        fields = '__all__'

class ProjServiceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = projServices
        fields = '__all__'

class ProjFinanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = finance
        exclude = ('deleteduser','deletedtime','createuser','createdtime','lastmodifyuser','lastmodifytime',)

class ProjAttachmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = attachment
        fields = '__all__'

class ProjAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = attachment
        exclude = ('deleteduser', 'deletedtime', 'createuser', 'createdtime', 'lastmodifyuser', 'lastmodifytime',)


class ProjSerializer(serializers.ModelSerializer):
    supportUser = UserCommenSerializer()
    proj_finances = ProjFinanceSerializer(many=True)
    proj_attachment = ProjAttachmentSerializer(many=True)
    class Meta:
        model = project
        exclude = ('isSendEmail','datasource')
        depth = 1

class ProjCommonSerializer(serializers.ModelSerializer):
    supportUser = ()
    tags = serializers.SerializerMethodField()
    industries = serializers.SerializerMethodField()
    class Meta:
        model = project
        fields = ('id','industries','projtitleC','projtitleE','tags','financeAmount','financeAmount_USD','country','projstatus','isHidden','ismarketplace','supportUser')
        depth = 1
    def get_tags(self, obj):
        qs = obj.tags.filter(tag_projects__is_deleted=False)
        if qs.exists():
            return tagSerializer(qs,many=True).data
        return None
    def get_industries(self, obj):
        qs = obj.project_industries.filter(is_deleted=False)
        if qs.exists():
            return ProjIndustrySerializer(qs,many=True).data
        return None

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
    # finance = serializers.SerializerMethodField()
    # attachment = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    industries = serializers.SerializerMethodField()
    transactionType = serializers.SerializerMethodField()
    class Meta:
        model = project
        fields = ('id','industries','projtitleC','projtitleE', 'transactionType','tags','financeAmount','financeAmount_USD','country','projstatus','isHidden','ismarketplace')
        depth = 1
    def get_tags(self, obj):
        qs = obj.tags.filter(tag_projects__is_deleted=False)
        if qs.exists():
            return tagSerializer(qs,many=True).data
        return None
    def get_industries(self, obj):
        qs = obj.project_industries.filter(is_deleted=False)
        if qs.exists():
            return ProjIndustrySerializer(qs,many=True).data
        return None
    def get_transactionType(self, obj):
        qs = obj.transactionType.filter(transactionType_projects__is_deleted=False)
        if qs.exists():
            return transactionTypeSerializer(qs,many=True).data
        return None

    def get_finance(self, obj):
        usertrader = obj.proj_finances.filter(is_deleted=False)
        if usertrader.exists():
            return FinanceSerializer(usertrader,many=True).data
        return None

    def get_attachment(self, obj):
        usertrader = obj.proj_attachment.filter(is_deleted=False)
        if usertrader.exists():
            return ProjAttachmentSerializer(usertrader, many=True).data
        return None

class ProjListSerializer_user(serializers.ModelSerializer):
    tags = serializers.SerializerMethodField()
    industries = serializers.SerializerMethodField()
    transactionType = serializers.SerializerMethodField()
    class Meta:
        model = project
        depth = 1
        fields = ('id','industries','projtitleC','projtitleE','tags','transactionType','financeAmount','financeAmount_USD','country','projstatus', 'ismarketplace')
    def get_tags(self, obj):
        qs = obj.tags.filter(tag_projects__is_deleted=False)
        if qs.exists():
            return tagSerializer(qs,many=True).data
        return None
    def get_industries(self, obj):
        qs = obj.project_industries.filter(is_deleted=False)
        if qs.exists():
            return ProjIndustrySerializer(qs,many=True).data
        return None

    def get_transactionType(self, obj):
        qs = obj.transactionType.filter(transactionType_projects__is_deleted=False)
        if qs.exists():
            return transactionTypeSerializer(qs,many=True).data
        return None
#detail
class ProjDetailSerializer_admin_withsecretinfo(serializers.ModelSerializer):
    finance = serializers.SerializerMethodField()
    attachment = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    service = serializers.SerializerMethodField()
    industries = serializers.SerializerMethodField()
    transactionType = serializers.SerializerMethodField()
    supportUser = UserCommenSerializer()
    takeUser = UserCommenSerializer()
    makeUser = UserCommenSerializer()
    linkpdfurl = serializers.SerializerMethodField()

    class Meta:
        model = project
        exclude = ('createuser', 'lastmodifyuser', 'deleteduser', 'deletedtime', 'datasource','isSendEmail',)
        depth = 1
    def get_tags(self, obj):
        qs = obj.tags.filter(tag_projects__is_deleted=False)
        if qs.exists():
            return tagSerializer(qs,many=True).data
        return None
    def get_service(self, obj):
        qs = obj.service.filter(service_projects__is_deleted=False)
        if qs.exists():
            return serviceSerializer(qs,many=True).data
        return None

    def get_industries(self, obj):
        qs = obj.project_industries.filter(is_deleted=False)
        if qs.exists():
            return ProjIndustrySerializer(qs,many=True).data
        return None
    def get_transactionType(self, obj):
        qs = obj.transactionType.filter(transactionType_projects__is_deleted=False)
        if qs.exists():
            return transactionTypeSerializer(qs,many=True).data
        return None
    def get_finance(self, obj):
        usertrader = obj.proj_finances.filter(is_deleted=False)
        if usertrader.exists():
            return FinanceSerializer(usertrader, many=True).data
        return None

    def get_attachment(self, obj):
        usertrader = obj.proj_attachment.filter(is_deleted=False)
        if usertrader.exists():
            return ProjAttachmentSerializer(usertrader, many=True).data
        return None
    def get_linkpdfurl(self, obj):
        if obj.linkpdfkey and obj.ismarketplace:
            return getUrlWithBucketAndKey('file',obj.linkpdfkey)
        return None

class ProjDetailSerializer_user_withsecretinfo(serializers.ModelSerializer):
    tags = serializers.SerializerMethodField()
    service = serializers.SerializerMethodField()
    industries = serializers.SerializerMethodField()
    transactionType = serializers.SerializerMethodField()
    finance = serializers.SerializerMethodField()
    attachment = serializers.SerializerMethodField()
    supportUser = UserCommenSerializer()
    takeUser = UserCommenSerializer()
    makeUser = UserCommenSerializer()
    class Meta:
        model = project
        exclude = ('createuser', 'lastmodifyuser', 'deleteduser', 'deletedtime', 'datasource','isSendEmail')
        depth = 1
    def get_tags(self, obj):
        qs = obj.tags.filter(tag_projects__is_deleted=False)
        if qs.exists():
            return tagSerializer(qs,many=True).data
        return None
    def get_industries(self, obj):
        qs = obj.project_industries.filter(is_deleted=False)
        if qs.exists():
            return ProjIndustrySerializer(qs,many=True).data
        return None
    def get_transactionType(self, obj):
        qs = obj.transactionType.filter(transactionType_projects__is_deleted=False)
        if qs.exists():
            return transactionTypeSerializer(qs,many=True).data
        return None
    def get_finance(self, obj):
        usertrader = obj.proj_finances.filter(is_deleted=False)
        if usertrader.exists():
            return FinanceSerializer(usertrader, many=True).data
        return None

    def get_attachment(self, obj):
        usertrader = obj.proj_attachment.filter(is_deleted=False)
        if usertrader.exists():
            return ProjAttachmentSerializer(usertrader, many=True).data
        return None
    def get_service(self, obj):
        qs = obj.service.filter(service_projects__is_deleted=False)
        if qs.exists():
            return serviceSerializer(qs,many=True).data
        return None


class ProjDetailSerializer_admin_withoutsecretinfo(serializers.ModelSerializer):
    tags = serializers.SerializerMethodField()
    service = serializers.SerializerMethodField()
    industries = serializers.SerializerMethodField()
    transactionType = serializers.SerializerMethodField()
    finance = serializers.SerializerMethodField()
    attachment = serializers.SerializerMethodField()
    supportUser = UserCommenSerializer()
    takeUser = UserCommenSerializer()
    makeUser = UserCommenSerializer()
    class Meta:
        model = project
        exclude = ('phoneNumber', 'email', 'contactPerson','createuser', 'lastmodifyuser', 'deleteduser', 'deletedtime', 'datasource','isSendEmail')
        depth = 1

    def get_service(self, obj):
        qs = obj.service.filter(service_projects__is_deleted=False)
        if qs.exists():
            return serviceSerializer(qs, many=True).data
        return None
    def get_tags(self, obj):
        qs = obj.tags.filter(tag_projects__is_deleted=False)
        if qs.exists():
            return tagSerializer(qs,many=True).data
        return None
    def get_industries(self, obj):
        qs = obj.project_industries.filter(is_deleted=False)
        if qs.exists():
            return ProjIndustrySerializer(qs,many=True).data
        return None
    def get_transactionType(self, obj):
        qs = obj.transactionType.filter(transactionType_projects__is_deleted=False)
        if qs.exists():
            return transactionTypeSerializer(qs,many=True).data
        return None
    def get_finance(self, obj):
        usertrader = obj.proj_finances.filter(is_deleted=False)
        if usertrader.exists():
            return FinanceSerializer(usertrader, many=True).data
        return None

    def get_attachment(self, obj):
        usertrader = obj.proj_attachment.filter(is_deleted=False)
        if usertrader.exists():
            return ProjAttachmentSerializer(usertrader, many=True).data
        return None
class ProjDetailSerializer_user_withoutsecretinfo(serializers.ModelSerializer):
    tags = serializers.SerializerMethodField()
    service = serializers.SerializerMethodField()
    industries = serializers.SerializerMethodField()
    transactionType = serializers.SerializerMethodField()
    finance = serializers.SerializerMethodField()
    attachment = serializers.SerializerMethodField()
    supportUser = UserCommenSerializer()
    takeUser = UserCommenSerializer()
    makeUser = UserCommenSerializer()
    class Meta:
        model = project
        exclude = ('phoneNumber', 'email', 'contactPerson','createuser', 'lastmodifyuser', 'deleteduser', 'deletedtime', 'datasource','isSendEmail')
        depth = 1

    def get_service(self, obj):
        qs = obj.service.filter(service_projects__is_deleted=False)
        if qs.exists():
            return serviceSerializer(qs, many=True).data
        return None
    def get_tags(self, obj):
        qs = obj.tags.filter(tag_projects__is_deleted=False)
        if qs.exists():
            return tagSerializer(qs,many=True).data
        return None
    def get_industries(self, obj):
        qs = obj.project_industries.filter(is_deleted=False)
        if qs.exists():
            return ProjIndustrySerializer(qs,many=True).data
        return None
    def get_transactionType(self, obj):
        qs = obj.transactionType.filter(transactionType_projects__is_deleted=False)
        if qs.exists():
            return transactionTypeSerializer(qs,many=True).data
        return None
    def get_finance(self, obj):
        usertrader = obj.proj_finances.filter(is_deleted=False)
        if usertrader.exists():
            return FinanceSerializer(usertrader, many=True).data
        return None

    def get_attachment(self, obj):
        usertrader = obj.proj_attachment.filter(is_deleted=False)
        if usertrader.exists():
            return ProjAttachmentSerializer(usertrader, many=True).data
        return None