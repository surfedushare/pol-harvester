from rest_framework import generics

from datagrowth.datatypes.views import CollectionBaseSerializer, CollectionBaseContentView
from pol_harvester.models import Document, Freeze
from pol_harvester.views.document import DocumentSerializer
from pol_harvester.views.annotation import AnnotationSerializer


class FreezeSerializer(CollectionBaseSerializer):

    content = DocumentSerializer(many=True, source="documents")
    annotations = AnnotationSerializer(many=True)

    class Meta:
        model = Freeze
        fields = CollectionBaseSerializer.default_fields + ("annotations",)


class FreezeView(generics.RetrieveAPIView):
    queryset = Freeze.objects.all()
    serializer_class = FreezeSerializer


class FreezeContentView(CollectionBaseContentView):
    queryset = Freeze.objects.all()
    content_class = Document
