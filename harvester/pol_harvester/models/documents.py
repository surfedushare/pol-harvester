import os
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib

from django.conf import settings
from django.db import models
from django.contrib.postgres import fields as postgres_fields
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from datagrowth import settings as datagrowth_settings
from datagrowth.datatypes import DocumentBase, DocumentPostgres, CollectionBase, DocumentCollectionMixin


class Freeze(DocumentCollectionMixin, CollectionBase):

    def init_document(self, data, collection=None):
        doc = super().init_document(data, collection=collection)
        doc.freeze = self
        return doc

    def __str__(self):
        return "{} (id={})".format(self.name, self.id)

    def get_elastic_indices(self):
        return ",".join([index.remote_name for index in self.indices.all()])

    def create_tfidf_vectorizer(self):
        if not self.name:
            raise ValueError("Can't create a vectorizer without a freeze name")
        vec = TfidfVectorizer(max_df=0.7)
        vec.fit_transform([doc.properties["text"] for doc in self.documents.all() if doc.properties["text"]])
        # Store to disk
        dst = os.path.join(datagrowth_settings.DATAGROWTH_DATA_DIR, self.name)
        os.makedirs(dst, exist_ok=True)
        joblib.dump(vec, os.path.join(dst, "tfidf.pkl"))

    def get_tfidf_vectorizer(self):
        src = os.path.join(datagrowth_settings.DATAGROWTH_DATA_DIR, self.name, "tfidf.pkl")
        vec = None
        try:
            vec = joblib.load(src)
        except FileNotFoundError:
            pass
        return vec

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


class Document(DocumentBase, DocumentPostgres):

    freeze = models.ForeignKey("Freeze", blank=True, null=True)
    # NB: Collection foreign key is added by the base class
    arrangement = models.ForeignKey("Arrangement", blank=True, null=True)

    def to_search(self):
        meta = self.arrangement.meta
        keys = meta.keys()

        # we add all the keys with a prefix, except for the 'pipeline'
        for key in keys:
            if key == 'documents':
                continue
            if key == 'pipeline':
                self.properties[key] = meta[key]
            else:
                self.properties[f'arrangement_{key}'] = meta[key]
        # we pick the language by looking at a few language sources
        language = None
        for field in ['from_text', 'from_title', 'metadata']:
            if field in self.properties['language']:
                language = self.properties['language'][field]
                if language is not None:
                    break

        # these dicts are compatible with Elastic Search
        return {
            'title': self.properties['title'],
            'text': self.properties['text'],
            'url': self.properties['url'],
            'language': language,
            'title_plain': self.properties['title'],
            'text_plain': self.properties['text'],
            'keywords': self.properties['arrangement_keywords'],
            'humanized_mime_type': settings.HUMANIZED_MIME_TYPES.get(self.properties['mime_type'], 'unknown'),
            'mime_type': self.properties['mime_type'],
            '_id': self.properties['id'],
            'arrangement_collection_name': self.collection.name
        }


class DocumentSitemap(Sitemap):

    changefreq = "never"
    priority = 1  # Google ignores this

    def __init__(self, freeze_name):
        self.freeze_name = freeze_name

    def items(self):
        return Document.objects.filter(freeze__name=self.freeze_name)

    def lastmod(self, obj):
        return obj.modified_at

    def location(self, obj):
        return reverse("content-document-html", args=(obj.id,))
