from rest_framework_mongoengine.serializers import DocumentSerializer

from mongoDoc.models import GroupEmailData, IMChatMessages, ProjectData, MergeFinanceData, CompanyCatData, ProjRemark, \
    WXChatdata


class CompanyCatDataSerializer(DocumentSerializer):
    class Meta:
        model = CompanyCatData
        fields = '__all__'

class MergeFinanceDataSerializer(DocumentSerializer):
    class Meta:
        model = MergeFinanceData
        fields = '__all__'

class ProjectDataSerializer(DocumentSerializer):
    class Meta:
        model = ProjectData
        fields = '__all__'

class ProjRemarkSerializer(DocumentSerializer):
    class Meta:
        model = ProjRemark
        fields = '__all__'

class GroupEmailDataSerializer(DocumentSerializer):
    class Meta:
        model = GroupEmailData
        fields = '__all__'

class IMChatMessagesSerializer(DocumentSerializer):
    class Meta:
        model = IMChatMessages
        fields = '__all__'

class WXChatdataSerializer(DocumentSerializer):
    class Meta:
        model = WXChatdata
        fields = '__all__'