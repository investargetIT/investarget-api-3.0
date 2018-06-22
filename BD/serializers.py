from django.db.models import Q
from rest_framework import serializers

from BD.models import ProjectBDComments, ProjectBD, OrgBDComments, OrgBD, MeetingBD
from org.serializer import OrgCommonSerializer
from proj.serializer import ProjSimpleSerializer
from sourcetype.serializer import BDStatusSerializer, orgAreaSerializer, tagSerializer
from sourcetype.serializer import titleTypeSerializer
from third.views.qiniufile import getUrlWithBucketAndKey
from usersys.serializer import UserCommenSerializer, UserRemarkSimpleSerializer, UserAttachmentSerializer


class ProjectBDCommentsCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectBDComments
        fields = '__all__'


class ProjectBDCommentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectBDComments
        fields = ('comments','id','createdtime','projectBD')


class ProjectBDCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectBD
        fields = '__all__'


class ProjectBDSerializer(serializers.ModelSerializer):
    BDComments = serializers.SerializerMethodField()
    location = orgAreaSerializer()
    usertitle = titleTypeSerializer()
    bd_status = BDStatusSerializer()
    manager = UserCommenSerializer()

    class Meta:
        model = ProjectBD
        exclude = ('deleteduser', 'deletedtime', 'datasource', 'is_deleted')

    def get_BDComments(self, obj):
        qs = obj.ProjectBD_comments.filter(is_deleted=False)
        if qs.exists():
            return ProjectBDCommentsSerializer(qs,many=True).data
        return None


class OrgBDCommentsCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrgBDComments
        fields = '__all__'


class OrgBDCommentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrgBDComments
        fields = ('comments','id','createdtime','orgBD')


class OrgBDCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrgBD
        fields = '__all__'


class OrgBDSerializer(serializers.ModelSerializer):
    org = OrgCommonSerializer()
    proj = ProjSimpleSerializer()
    BDComments = serializers.SerializerMethodField()
    usertitle = titleTypeSerializer()
    bd_status = BDStatusSerializer()
    cardurl = serializers.SerializerMethodField()
    userreamrk = serializers.SerializerMethodField()
    userattachment = serializers.SerializerMethodField()
    manager = UserCommenSerializer()
    userinfo = serializers.SerializerMethodField()
    createuser = UserCommenSerializer()
    makeUser = serializers.SerializerMethodField()

    class Meta:
        model = OrgBD
        exclude = ('deleteduser', 'deletedtime', 'datasource', 'is_deleted', 'usermobile')

    def get_BDComments(self, obj):
        qs = obj.OrgBD_comments.filter(is_deleted=False)
        if qs.exists():
            return OrgBDCommentsSerializer(qs,many=True).data
        return None

    def get_cardurl(self, obj):
        if obj.bduser:
            if obj.bduser.cardKey:
                return 'https://o79atf82v.qnssl.com/' + obj.bduser.cardKey
        return None

    def get_userreamrk(self, obj):
        if obj.bduser:
            return UserRemarkSimpleSerializer(obj.bduser.user_remarks.all(), many=True).data
        return None

    def get_userattachment(self, obj):
        if obj.bduser:
            return UserAttachmentSerializer(obj.bduser.user_userAttachments.all(), many=True).data
        return None

    def get_wechat(self, obj):
        if obj.bduser:
            return obj.bduser.wechat
        return None

    def get_email(self, obj):
        if obj.bduser:
            return obj.bduser.email
        return None

    def get_userinfo(self, obj):
        user_id = self.context.get("user_id")
        info = {'email': None, 'mobile': None, 'wechat': None, 'tags':None, 'photourl': None}
        if obj.bduser:
            tags = obj.bduser.tags.filter(tag_usertags__is_deleted=False)
            if tags.exists():
                info['tags'] = tagSerializer(tags, many=True).data
            if obj.bduser.photoKey:
                info['photourl'] = getUrlWithBucketAndKey('image', obj.bduser.photoKey)
            if user_id:
                filterset = Q(familiar__score__gte=1) | Q(traderuser_id=user_id)
            else:
                filterset = Q(familiar__score__gte=1)
            if not obj.bduser.investor_relations.all().filter(filterset).exists():
                    info = {
                        'email': obj.bduser.email,
                        'mobile': obj.bduser.mobile,
                        'wechat': obj.bduser.wechat,
                    }
        return info

    def get_makeUser(self, obj):
        if obj.proj:
            if obj.proj.makeUser:
                return obj.proj.makeUser_id
        return None


class MeetingBDCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingBD
        fields = '__all__'


class MeetingBDSerializer(serializers.ModelSerializer):
    org = OrgCommonSerializer()
    proj = ProjSimpleSerializer()
    usertitle = titleTypeSerializer()
    manager = UserCommenSerializer()
    attachmenturl = serializers.SerializerMethodField()

    class Meta:
        model = MeetingBD
        exclude = ('deleteduser', 'deletedtime', 'datasource', 'is_deleted', 'createuser')

    def get_attachmenturl(self, obj):
        if obj.attachmentbucket and obj.attachment:
            return getUrlWithBucketAndKey(obj.attachmentbucket, obj.attachment)
        else:
            return None
