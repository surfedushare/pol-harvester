import os
from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib
from collections import Iterator

from django.db import models
from django.contrib.postgres import fields as postgres_fields
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils.timezone import now

from datagrowth import settings as datagrowth_settings
from datagrowth.utils import ibatch
from datagrowth.datatypes import DocumentBase, DocumentPostgres, CollectionBase, DocumentCollectionMixin


class Freeze(DocumentCollectionMixin, CollectionBase):

    is_active = models.BooleanField(default=False)

    def init_document(self, data, collection=None):
        doc = super().init_document(data, collection=collection)
        doc.freeze = self
        return doc

    def __str__(self):
        return "{} (id={})".format(self.name, self.id)

    @classmethod
    def get_name(cls):
        return "freeze"

    def reset(self):
        self.collection_set.all().delete()
        for harvest in self.edurepharvest_set.all():
            harvest.reset()

    def get_elastic_indices(self):
        return ",".join([index.remote_name for index in self.indices.all()])

    def get_earliest_harvest_date(self):
        latest_harvest = self.edurepharvest_set.order_by("harvested_at").first()
        return latest_harvest.harvested_at if latest_harvest else None

    def get_elastic_documents_by_language(self, since):
        by_language = defaultdict(list)
        for arrangement in self.arrangement_set.prefetch_related("document_set").filter(modified_at__gte=since):
            languages = {doc.get_language() for doc in arrangement.documents.all()}
            if len(languages) != 1:
                print(f"Impossible to determine language for arrangement: {arrangement.id}")
                continue
            language = languages.pop()
            by_language[language].append(arrangement.to_search())
        return by_language

    def get_documents_by_language(self, as_search=False, minimal_educational_level=-1):
        by_language = defaultdict(list)
        for doc in self.documents.all():
            if doc.properties.get("lowest_educational_level", -1) < minimal_educational_level:
                continue
            language = doc.get_language()
            by_language[language].append(doc if not as_search else doc.to_search())
        return by_language

    def create_tfidf_vectorizers(self):
        if not self.name:
            raise ValueError("Can't create a vectorizer without a freeze name")
        dst = os.path.join(datagrowth_settings.DATAGROWTH_DATA_DIR, self.name)
        os.makedirs(dst, exist_ok=True)

        for language, docs in self.get_documents_by_language().items():
            vec = TfidfVectorizer(max_df=0.7)
            vec.fit_transform([doc.properties["text"] for doc in docs if doc.properties["text"]])
            joblib.dump(vec, os.path.join(dst, f"tfidf.{language}.pkl"))

    def get_tfidf_vectorizer(self, language):
        src = os.path.join(datagrowth_settings.DATAGROWTH_DATA_DIR, self.name, f"tfidf.{language}.pkl")
        vec = None
        try:
            vec = joblib.load(src)
        except FileNotFoundError:
            pass
        return vec


class Collection(DocumentCollectionMixin, CollectionBase):

    freeze = models.ForeignKey("Freeze", blank=True, null=True, on_delete=models.CASCADE)

    def init_document(self, data, collection=None):
        doc = super().init_document(data, collection=collection)
        doc.freeze = self.freeze
        return doc

    def __str__(self):
        return "{} (id={})".format(self.name, self.id)


class Arrangement(DocumentCollectionMixin, CollectionBase):

    freeze = models.ForeignKey("Freeze", blank=True, null=True, on_delete=models.CASCADE)
    collection = models.ForeignKey("Collection", blank=True, null=True, on_delete=models.CASCADE)
    meta = postgres_fields.JSONField(default=dict)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def init_document(self, data, collection=collection):
        doc = super().init_document(data, collection=collection)
        doc.freeze = self.freeze
        doc.arrangement = self
        return doc

    def update(self, data, by_reference, validate=True, batch_size=32, collection=None):
        collection = collection or self
        Document = collection.get_document_model()
        assert isinstance(data, (Iterator, list, tuple, dict, Document)), \
            f"Collection.update expects data to be formatted as iteratable, dict or {type(Document)} not {type(data)}"

        count = 0
        for updates in ibatch(data, batch_size=batch_size):
            # First we bulk update by getting all objects whose identifier value match any update's "by" value
            # and then updating these source objects.
            # One update object can potentially target multiple sources
            # if multiple objects with an identifier of "by" exist.
            updated = set()
            hashed = {update[by_reference]: update for update in updates}
            sources = {source[by_reference]: source for source in collection.documents.filter(reference__in=hashed.keys())}
            for source in sources.values():
                source.update(hashed[source.reference], validate=validate)
                count += 1
                updated.add(source.reference)
            Document.objects.bulk_update(
                sources.values(),
                ["properties"],
                batch_size=datagrowth_settings.DATAGROWTH_MAX_BATCH_SIZE
            )
            # After all updates we add all data that hasn't been used in any update operation
            additions = [update for identify, update in hashed.items() if identify not in updated]
            if len(additions):
                count += self.add(additions, validate=validate, batch_size=batch_size, collection=collection)

        return count

    def to_search(self):

        text_documents = self.documents.exclude(properties__file_type="video")
        texts = []
        for doc in text_documents:
            texts.append(doc.properties["text"])
        text = "\n\n".join(texts)

        video_documents = self.documents.filter(properties__file_type="video")
        transcriptions = []
        for doc in video_documents:
            if doc.properties["text"] is None:
                continue
            transcriptions.append(doc.properties["text"])
        transcription = "\n\n".join(transcriptions)

        base_document = video_documents.first()
        if base_document is None:
            base_document = text_documents.first()

        # Elastic Search actions get streamed to the Elastic Search service
        elastic_search_action = {
            'title': base_document.properties['title'],
            'text': text,
            'transcription': transcription,
            'url': base_document.properties['url'],
            'external_id': base_document.properties['external_id'],
            'disciplines': base_document.properties['disciplines'],
            'educational_levels': base_document.properties['educational_levels'],
            'lom_educational_levels': base_document.properties['lom_educational_levels'],
            'author': base_document.properties['author'],
            'authors': base_document.properties['authors'],
            'publishers': base_document.properties['publishers'],
            'description': base_document.properties['description'],
            'publisher_date': base_document.properties['publisher_date'],
            'copyright': base_document.properties['copyright'],
            'language': base_document.get_language(),
            'title_plain': base_document.properties['title'],
            'text_plain': text,
            'transcription_plain': transcription,
            'keywords': self.meta['keywords'],
            'file_type': base_document['file_type'] if 'file_type' in base_document.properties else 'unknown',
            'mime_type': base_document['mime_type'],
            'suggest': base_document['title'].split(" ") if base_document['title'] else [],
            '_id': self.meta['reference_id'],
            'arrangement_collection_name': self.collection.name  # TODO: migrate to just collection name
        }
        if self.deleted_at:
            elastic_search_action["_op_type"] = "delete"
        return elastic_search_action

    def restore(self):
        self.deleted_at = None
        self.save()

    def delete(self, using=None, keep_parents=False):
        if not self.deleted_at:
            self.deleted_at = now()
            self.save()
        else:
            super().delete(using=using, keep_parents=keep_parents)


class Document(DocumentPostgres, DocumentBase):

    freeze = models.ForeignKey("Freeze", blank=True, null=True, on_delete=models.CASCADE)
    # NB: Collection foreign key is added by the base class
    arrangement = models.ForeignKey("Arrangement", blank=True, null=True, on_delete=models.CASCADE)

    def get_language(self):
        for field in ['from_text', 'from_title', 'metadata']:
            if field in self.properties['language']:
                language = self.properties['language'][field]
                if language is not None:
                    return language

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

        # these dicts are compatible with Elastic Search
        return {
            'title': self.properties['title'],
            'text': self.properties['text'],
            'url': self.properties['url'],
            'external_id': self.properties['external_id'],
            'disciplines': self.properties['disciplines'],
            'educational_levels': self.properties['educational_levels'],
            'author': self.properties['author'],
            'description': self.properties['description'],
            'publisher_date': self.properties['publisher_date'],
            'copyright': self.properties['copyright'],
            'language': self.get_language(),
            'title_plain': self.properties['title'],
            'text_plain': self.properties['text'],
            'description_plain': self.properties['description'],
            'keywords': self.properties['arrangement_keywords'],
            'file_type': self.properties.get('file_type', 'unknown'),
            'mime_type': self.properties['mime_type'],
            'suggest': self.properties['title'].split(" ") if self.properties['title'] else [],
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
