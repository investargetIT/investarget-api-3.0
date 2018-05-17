from rest_framework import serializers

from BD.models import ProjectBDComments, ProjectBD, OrgBDComments, OrgBD, MeetingBD
from org.serializer import OrgCommonSerializer
from proj.serializer import ProjSimpleSerializer
from sourcetype.serializer import BDStatusSerializer, orgAreaSerializer
from sourcetype.serializer import titleTypeSerializer
from third.views.qiniufile import getUrlWithBucketAndKey
from usersys.serializer import UserCommenSerializer


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
    manager = UserCommenSerializer()
    wechat = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    useinfo = serializers.SerializerMethodField()
    createuser = UserCommenSerializer()
    makeUser = serializers.SerializerMethodField()

    class Meta:
        model = OrgBD
        exclude = ('deleteduser', 'deletedtime', 'datasource', 'is_deleted')

    def get_BDComments(self, obj):
        qs = obj.OrgBD_comments.filter(is_deleted=False)
        if qs.exists():
            return OrgBDCommentsSerializer(qs,many=True).data
        return None

    def get_wechat(self, obj):
        if obj.bduser:
            return obj.bduser.wechat
        return None

    def get_email(self, obj):
        if obj.bduser:
            return obj.bduser.email
        return None

    def get_useinfo(self, obj):
        if obj.bduser:
            return UserCommenSerializer(obj.bduser).data
        return None

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
