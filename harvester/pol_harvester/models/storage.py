from django.conf import settings
from django.db import models
from django.contrib.postgres import fields as postgres_fields

from datagrowth.datatypes import DocumentBase, DocumentPostgres, CollectionBase, DocumentCollectionMixin


class Freeze(DocumentCollectionMixin, CollectionBase):

    def init_document(self, data, collection=None):
        doc = super().init_document(data, collection=collection)
        doc.freeze = self
        return doc

    def __str__(self):
        return "{} (id={})".format(self.name, self.id)


class Collection(DocumentCollectionMixin, CollectionBase):

    freeze = models.ForeignKey("Freeze", blank=True, null=True)

    def init_document(self, data, collection=None):
        doc = super().init_document(data, collection=collection)
        doc.freeze = self.freeze
        return doc

    def __str__(self):
        return "{} (id={})".format(self.name, self.id)


class Arrangement(DocumentCollectionMixin, CollectionBase):

    freeze = models.ForeignKey("Freeze", blank=True, null=True)
    collection = models.ForeignKey("Collection", blank=True, null=True)
    meta = postgres_fields.JSONField(default=dict)

    def init_document(self, data, collection=collection):
        doc = super().init_document(data, collection=collection)
        doc.freeze = self.freeze
        doc.arrangement = self
        return doc

    def to_dicts(self):
        keys = self.meta.keys()
        for dictionary in self.content:
            # we add all the keys with a prefix, except for the 'pipeline'
            for key in keys:
                if key == 'documents':
                    continue
                if key == 'pipeline':
                    dictionary[key] = self.meta[key]
                else:
                    dictionary[f'arrangement_{key}'] = self.meta[key]
            if "pipeline" in dictionary:
                del dictionary["pipeline"]
            dictionary["title_plain"] = dictionary["title"]
            dictionary["text_plain"] = dictionary["text"]
            dictionary["keywords"] = dictionary["arrangement_keywords"]
            dictionary["arrangement_collection_name"] = self.collection.name
            dictionary["humanized_mime_type"] = settings.HUMANIZED_MIME_TYPES.get(dictionary['mime_type'], 'unknown')
            dictionary["_id"] = dictionary['id']
            yield dictionary


class Document(DocumentBase, DocumentPostgres):

    freeze = models.ForeignKey("Freeze", blank=True, null=True)
    # NB: Collection foreign key is added by the base class
    arrangement = models.ForeignKey("Arrangement", blank=True, null=True)
