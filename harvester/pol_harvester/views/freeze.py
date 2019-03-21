from rest_framework import generics

from datagrowth.datatypes.views import CollectionBaseSerializer, CollectionBaseContentView
from pol_harvester.models import Document, Freeze
from pol_harvester.views.document import DocumentSerializer
from pol_harvester.views.annotation import AnnotationSerializer


class FreezeDetailSerializer(CollectionBaseSerializer):

    content = DocumentSerializer(many=True, source="documents")
    annotations = AnnotationSerializer(many=True)

    class Meta:
        model = Freeze
        fields = CollectionBaseSerializer.default_fields + ("content", "annotations",)


class FreezeListSerializer(CollectionBaseSerializer):

    class Meta:
        model = Freeze
        fields = CollectionBaseSerializer.default_fields


class FreezeListView(generics.ListAPIView):
    queryset = Freeze.objects.all()
    serializer_class = FreezeListSerializer


class FreezeDetailView(generics.RetrieveAPIView):
    queryset = Freeze.objects.all()
    serializer_class = FreezeDetailSerializer


class FreezeContentView(CollectionBaseContentView):
    queryset = Freeze.objects.all()
    content_class = Document
