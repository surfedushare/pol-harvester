from django.shortcuts import render, Http404
from rest_framework import generics

from datagrowth.datatypes.views import ContentView, ContentSerializer, DocumentBaseSerializer
from pol_harvester.models import Document


class DocumentSerializer(DocumentBaseSerializer):

    class Meta:
        model = Document
        fields = DocumentBaseSerializer.default_fields


class DocumentView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer


class DocumentContentView(ContentView, generics.UpdateAPIView):
    queryset = Document.objects.all()
    serializer_class = ContentSerializer
    content_class = Document


def document_html_view(request, pk):
    try:
        document = Document.objects.get(id=pk)
    except Document.DoesNotExist:
        raise Http404("Document not found")
    return render(request, "pol_harvester/document.html", context={
        "document": document.to_search()
    })
