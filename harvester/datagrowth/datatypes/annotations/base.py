from django.conf import settings
from django.db import models



class AnnotationBase(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
    reference = models.CharField(max_length=255, db_index=True)
    name = models.CharField(max_length=255, db_index=True)
    value = models.FloatField(blank=True, null=True)
    string = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    @property
    def annotation(self):
        return self.value if self.value is not None else self.string

    class Meta:
        abstract = True
