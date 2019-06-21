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

    def to_documents(self):
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
            # we pick the language by looking at a few language sources
            language = None
            for field in ['from_text', 'from_title', 'metadata']:
                if field in dictionary['language']:
                    language = dictionary['language'][field]
                    if language is not None:
                        break
            # these dicts are compatible with Elastic Search
            yield {
                'title': dictionary['title'],
                'text': dictionary['text'],
                'url': dictionary['url'],
                'language': language,
                'title_plain': dictionary['title'],
                'text_plain': dictionary['text'],
                'keywords': dictionary['arrangement_keywords'],
                'humanized_mime_type': settings.HUMANIZED_MIME_TYPES.get(dictionary['mime_type'], 'unknown'),
                'mime_type': dictionary['mime_type'],
                '_id': dictionary['id'],
                'arrangement_collection_name': dictionary['arrangement_collection_name']
            }


class Document(DocumentBase, DocumentPostgres):

    freeze = models.ForeignKey("Freeze", blank=True, null=True)
    # NB: Collection foreign key is added by the base class
    arrangement = models.ForeignKey("Arrangement", blank=True, null=True)
