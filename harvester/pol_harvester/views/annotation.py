from datagrowth.datatypes.views import AnnotationBaseSerializer, AnnotationBaseView
from pol_harvester.models import Annotation, Freeze
from .document import DocumentSerializer


class AnnotationSerializer(AnnotationBaseSerializer):

    class Meta:
        model = Annotation
        fields = AnnotationBaseSerializer.default_fields


class AnnotationView(AnnotationBaseView):
    collection_model = Freeze
    annotation_model = Annotation
    document_serializer = DocumentSerializer
