from rest_framework_mongoengine.serializers import DynamicDocumentSerializer, DocumentSerializer, EmbeddedDocumentSerializer

from mongoDoc.models import GroupEmailData, IMChatMessages, ProjectData, MergeFinanceData, CompanyCatData


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

class GroupEmailDataSerializer(DocumentSerializer):
    class Meta:
        model = GroupEmailData
        fields = '__all__'

class IMChatMessagesSerializer(DocumentSerializer):
    class Meta:
        model = IMChatMessages
        fields = '__all__'