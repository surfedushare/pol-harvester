from rest_framework import serializers


class AnnotationBaseSerializer(serializers.ModelSerializer):

    username = serializers.SerializerMethodField()

    default_fields = ("id", "created_at", "modified_at", "username", "reference", "name", "annotation")

    def get_username(self, annotation):
        return annotation.user.username if annotation.user is not None else None
