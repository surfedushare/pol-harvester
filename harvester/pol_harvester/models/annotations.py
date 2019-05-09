from django.db import models

from datagrowth.datatypes import AnnotationBase


class Annotation(AnnotationBase):
    string = models.TextField(blank=True, null=True)
