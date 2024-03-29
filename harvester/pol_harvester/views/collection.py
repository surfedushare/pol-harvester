from rest_framework import generics

from datagrowth.datatypes.views import CollectionBaseSerializer, CollectionBaseContentView
from pol_harvester.models import Collection, Document
from pol_harvester.views.document import DocumentSerializer


class CollectionSerializer(CollectionBaseSerializer):

    content = DocumentSerializer(many=True, source="documents")

    class Meta:
        model = Collection
        fields = CollectionBaseSerializer.default_fields + ("content",)


class CollectionView(generics.RetrieveAPIView):
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer


class CollectionContentView(CollectionBaseContentView):
    queryset = Collection.objects.all()
    content_class = Document
