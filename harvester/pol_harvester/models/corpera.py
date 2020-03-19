from django.apps import apps
from django.db import models

from datagrowth.datatypes import DocumentBase, DocumentPostgres, CollectionBase, DocumentCollectionMixin


class Corpus(DocumentCollectionMixin, CollectionBase):

    @classmethod
    def get_document_model(cls):
        # This method should use "Document" with local app label and get_model function to load the model
        return apps.get_model("{}.Article".format(cls._meta.app_label))

    def to_text_file(self, file_path):
        texts = [doc.properties["text"] for doc in self.documents.all() if doc.properties["text"]]
        with open(file_path, "w") as text_file:
            text_file.write("\n\n\n\n".join(texts))

    class Meta:
        verbose_name = "corpus"
        verbose_name_plural = "corpera"


class Article(DocumentBase, DocumentPostgres):

    # We link the Corpus through the collection property to document_set to leverage the Datagrowth package
    collection = models.ForeignKey("Corpus", blank=True, null=True, related_name="document_set",
                                   on_delete=models.CASCADE)
