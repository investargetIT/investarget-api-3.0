from rest_framework_mongoengine.serializers import DynamicDocumentSerializer, DocumentSerializer, EmbeddedDocumentSerializer

from mongoDoc.models import GroupEmailData, IMChatMessages


# class WXContentDataSerializer(DocumentSerializer):
#     class Meta:
#         model = WXContentData
#         fields = '__all__'

class GroupEmailDataSerializer(DocumentSerializer):
    class Meta:
        model = GroupEmailData
        fields = '__all__'

class IMChatMessagesSerializer(DocumentSerializer):
    class Meta:
        model = IMChatMessages
        fields = '__all__'