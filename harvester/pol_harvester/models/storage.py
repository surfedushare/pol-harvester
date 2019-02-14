from django.db import models
from django.contrib.postgres import fields as postgres_fields

from datagrowth.datatypes import DocumentBase, DocumentPostgres, CollectionBase


class Freeze(CollectionBase):

    def init_document(self, data, collection=None):
        doc = super().init_document(data, collection=collection)
        doc.freeze = self
        return doc


class Collection(CollectionBase):
    freeze = models.ForeignKey("Freeze", blank=True, null=True)

    def init_document(self, data, collection=None):
        doc = super().init_document(data, collection=collection)
        doc.freeze = self.freeze
        return doc


class Arrangement(CollectionBase):
    freeze = models.ForeignKey("Freeze", blank=True, null=True)
    collection = models.ForeignKey("Collection", blank=True, null=True)
    meta = postgres_fields.JSONField(default=dict)

    def init_document(self, data, collection=collection):
        doc = super().init_document(data, collection=collection)
        doc.freeze = self.freeze
        doc.arrangement = self
        return doc


class Document(DocumentBase, DocumentPostgres):
    freeze = models.ForeignKey("Freeze", blank=True, null=True)
    # NB: Collection foreign key is added by the base class
    arrangement = models.ForeignKey("Arrangement", blank=True, null=True)