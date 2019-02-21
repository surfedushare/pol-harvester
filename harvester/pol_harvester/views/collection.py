from rest_framework import generics

from datagrowth.datatypes.views import CollectionBaseSerializer, CollectionBaseContentView
from pol_harvester.models import Collection, Document
from pol_harvester.views.document import DocumentSerializer
from pol_harvester.views.annotation import AnnotationSerializer


class CollectionSerializer(CollectionBaseSerializer):

    content = DocumentSerializer(many=True, source="documents")
    annotations = AnnotationSerializer(many=True)

    class Meta:
        model = Collection
        fields = CollectionBaseSerializer.default_fields


class CollectionView(generics.RetrieveAPIView):
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer


class CollectionContentView(CollectionBaseContentView):
    queryset = Collection.objects.all()
    content_class = Document
