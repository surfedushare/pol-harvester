from datagrowth.datatypes.views import AnnotationBaseSerializer
from pol_harvester.models import Annotation


class AnnotationSerializer(AnnotationBaseSerializer):

    class Meta:
        model = Annotation
        fields = AnnotationBaseSerializer.default_fields
