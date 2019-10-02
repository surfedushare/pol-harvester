from elasticsearch.helpers import streaming_bulk

from django.conf import settings
from django.db import models
from django.utils.text import slugify
from django.contrib.postgres.fields import JSONField
from rest_framework import serializers

from pol_harvester.models import Freeze
from search.utils.elastic import get_index_config, get_es_client


elastic_client = get_es_client()


class ElasticIndex(models.Model):

    name = models.CharField(max_length=255)
    language = models.CharField(max_length=5, choices=settings.ELASTIC_SEARCH_ANALYSERS.items())
    freeze = models.ForeignKey(Freeze, related_name="indices")
    configuration = JSONField(blank=True)
    error_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = elastic_client

    @property
    def remote_name(self):
        if not self.id:
            raise ValueError("Can't get the remote name for an unsaved object")
        return slugify("{}-{}-{}".format(self.name, self.language, self.id))

    @property
    def remote_exists(self):
        if not self.id:
            raise ValueError("Can't check for existence with an unsaved object")
        return self.client.indices.exists(self.remote_name)

    def push(self, elastic_documents, recreate=True):
        if not self.id:
            raise ValueError("Can't push index with unsaved object")

        remote_name = self.remote_name
        if self.remote_exists and recreate:
            self.client.indices.delete(remote_name)

        self.client.indices.create(
            index=remote_name,
            body=self.configuration,
            request_timeout=300  # a bit of a workaround, why is the elastic cluster slow?
        )
        if recreate:
            self.error_count = 0
        for is_ok, result in streaming_bulk(self.client, elastic_documents, index=remote_name, doc_type="_doc",
                                            chunk_size=100, yield_ok=False, raise_on_error=False):
            if not is_ok:
                self.error_count += 1
                print(f'Error in sending bulk:{result}')
        self.save()

    def clean(self):
        if not self.name:
            self.name = self.freeze.name
        if self.language and not self.configuration:
            self.configuration = get_index_config(self.language)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "elastic index"
        verbose_name_plural = "elastic indices"


class ElasticIndexSerializer(serializers.ModelSerializer):

    class Meta:
        model = ElasticIndex
        fields = ("id", "name", "language", "remote_name",)
