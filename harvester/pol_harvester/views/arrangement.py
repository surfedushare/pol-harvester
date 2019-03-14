from rest_framework import generics

from datagrowth.datatypes.views import CollectionBaseSerializer, CollectionBaseContentView
from pol_harvester.models import Arrangement, Document
from pol_harvester.views.document import DocumentSerializer


class ArrangementSerializer(CollectionBaseSerializer):

    content = DocumentSerializer(many=True, source="documents")

    class Meta:
        model = Arrangement
        fields = CollectionBaseSerializer.default_fields


class ArrangementView(generics.RetrieveAPIView):
    queryset = Arrangement.objects.all()
    serializer_class = ArrangementSerializer


class ArrangementContentView(CollectionBaseContentView):
    queryset = Arrangement.objects.all()
    content_class = Document
