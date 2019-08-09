from django.apps import apps
from django.db import models

from datagrowth.datatypes import DocumentBase, DocumentPostgres, CollectionBase, DocumentCollectionMixin


class Corpus(DocumentCollectionMixin, CollectionBase):

    @classmethod
    def get_document_model(cls):
        # This method should use "Document" with local app label and get_model function to load the model
        return apps.get_model("{}.Article".format(cls._meta.app_label))


class Article(DocumentBase, DocumentPostgres):

    # We link the Corpus through the collection property to document_set to leverage the Datagrowth package
    collection = models.ForeignKey("Corpus", blank=True, null=True, related_name="document_set")
