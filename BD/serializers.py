from rest_framework import serializers

from BD.models import ProjectBDComments, ProjectBD, OrgBDComments, OrgBD, MeetingBD
from org.serializer import OrgCommonSerializer
from proj.serializer import ProjSimpleSerializer
from sourcetype.serializer import countrySerializer, BDStatusSerializer
from sourcetype.serializer import titleTypeSerializer
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
    location = countrySerializer()
    usertitle = titleTypeSerializer()
    bd_status = BDStatusSerializer()
    manager = UserCommenSerializer()

    class Meta:
        model = ProjectBD
        exclude = ('deleteduser', 'deletedtime', 'datasource', 'is_deleted','createuser')

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

    class Meta:
        model = OrgBD
        exclude = ('deleteduser', 'deletedtime', 'datasource', 'is_deleted','createuser')

    def get_BDComments(self, obj):
        qs = obj.OrgBD_comments.filter(is_deleted=False)
        if qs.exists():
            return OrgBDCommentsSerializer(qs,many=True).data
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

    class Meta:
        model = MeetingBD
        exclude = ('deleteduser', 'deletedtime', 'datasource', 'is_deleted', 'createuser')