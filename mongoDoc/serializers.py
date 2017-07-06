from rest_framework_mongoengine.serializers import DynamicDocumentSerializer, DocumentSerializer, EmbeddedDocumentSerializer

from mongoDoc.models import WXContentData


class WXContentDataSerializer(DocumentSerializer):
    class Meta:
        model = WXContentData
        fields = '__all__'

