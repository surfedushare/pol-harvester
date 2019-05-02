"""
Creates an index in elastic search.
We use the embedded elastic search config in the code.
See --help for options and arguments.
"""
import json
import os
from collections import defaultdict

from elasticsearch.helpers import streaming_bulk
from elasticsearch import Elasticsearch

from django.core.management.base import BaseCommand
from pol_harvester.models import Document
import logging

LANG_ORDER = ['from_text', 'from_title', 'metadata']
ANALYSERS = {
    'en': 'english',
    'nl': 'dutch'
}
HUMANIZED_MIME_TYPES = {
    'unknown': 'unknown',
    'application/pdf': 'pdf',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'powerp.',
    'application/vnd.ms-powerpoint': 'powerp.',
    'application/msword': 'word',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'word',
    'application/rtf': 'word',
    'text/plain': 'word',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'excel',
    'text/html': 'html',
    'video': 'video',
    'image': 'image',
    'application/zip': 'zip',
    'audio/mpeg': 'audio',
    'application/octet-stream': 'other'
}

log = logging.getLogger("freeze")


def get_index_config(lang):
    """
    Returns the elasticsearch index configuration.
    Configures the analysers based on the language passed in.
    """
    return {
        "settings": {
            "index": {
                "number_of_shards": 1,
                "number_of_replicas": 0
            }
        },
        'mappings': {
            '_doc': {
                'properties': {
                    'title': {
                        'type': 'text',
                        'analyzer': ANALYSERS[lang]
                    },
                    'text': {
                        'type': 'text',
                        'analyzer': ANALYSERS[lang]
                    },
                    'url': {'type': 'text'},
                    'title_plain': {'type': 'text'},
                    'text_plain': {'type': 'text'},
                    'keywords': {'type': 'text'},
                    'mime_type': {'type': 'text'},
                    'humanized_mime_type': {'type': 'text'},
                    'id': {'type': 'text'},
                    'arrangement_collection_name': {'type': 'text'}
                }
            }
        }
    }


def to_es_document(doc):
    """
    Returns a correctly formatted elasticsearch document from a given document.
    This needs to correspond correctly with the properties defined in the
    index.
    """
    return {
        'title': doc['title'],
        'text': doc['text'],
        'url': doc['url'],
        'title_plain': doc['title'],
        'text_plain': doc['text'],
        # 'keywords': doc['arrangement_keywords'], #todo do we need this?
        'humanized_mime_type': HUMANIZED_MIME_TYPES.get(doc['mime_type'],
                                                        'unknown'),
        'mime_type': doc['mime_type'],
        '_id': doc['id'],
        'arrangement_collection_name': doc['arrangement_collection_name']
    }


def bulk_insert_documents(client, index_name, documents):
    """
    Inserts a collection of documents to an index in bulk.
    """
    es_documents = (to_es_document(document) for document in documents)
    for is_ok, result in streaming_bulk(client,
                                        es_documents,
                                        index=index_name,
                                        doc_type="_doc",
                                        chunk_size=100,
                                        ):
        if not is_ok:
            print(f'Error in sending bulk:{result}')


def get_language(document):
    """
    Returns the language of the document, given a preference of fields
    """
    # The priority is in that order
    for field in LANG_ORDER:
        if field in document['language']:
            current_lang = document['language'][field]
            if current_lang is not None:
                return current_lang
    return "unknown"


def read_languages(folder):
    """
    Returns the languages defined the folder structure.
    """
    return [entity for entity in os.listdir(folder)]


def create_index(es, name, language, documents, recreate):
    index_name = f'{name}-{language}'
    log.info(f'Creating index: {index_name}')

    config = get_index_config(language)
    if es.indices.exists(index_name) and recreate:
        es.indices.delete(index_name)

    es.indices.create(
        index=index_name,
        body=config)
    bulk_insert_documents(es,
                          index_name,
                          documents)


def get_es_config(file_path):
    """
    Reads a json file containing the elastic search credentials and url.
    The file is expected to have 'url', 'username' and 'password' keys
    """

    with open(file_path) as stream:
        credentials = json.load(stream)
    return (credentials['url'],
            (credentials['username'], credentials['password']),
            credentials['host'])


def get_es_client(credentials_file):
    """
    Returns the elasticsearch client which uses the configuration file
    """

    _, auth, host = get_es_config(credentials_file)
    es_client = Elasticsearch([host],
                              http_auth=auth,
                              scheme='https',
                              port=443,
                              http_compress=True)
    # test if it works
    if not es_client.cat.health():
        raise ValueError('Credentials do not work for Elastic search')
    return es_client

class Command(BaseCommand):
    def handle(self, *args, **options):
        name = "freeze6-test"
        credentials_file = "../es_credentials.json"
        recreate = True

        documents = Document.objects.filter(freeze_id=10)  # 10 == freeze 6
        print(f"freeze 6 document count: {len(documents)}")

        for doc in documents:
            doc.properties['arrangement_collection_name'] = doc.collection.name

        lang_doc = ((get_language(doc.properties), doc.properties) for doc in documents)
        lang_doc_dict = defaultdict(list)
        # create a list so we can report counts
        for lang, doc in lang_doc:
            lang_doc_dict[lang].append(doc)
        for lang in lang_doc_dict.keys():
            log.info(f'{lang}:{len(lang_doc_dict[lang])}')
        es = get_es_client(credentials_file)
        [create_index(es, name, lang, lang_doc_dict[lang], recreate)
         for lang in lang_doc_dict.keys() if lang in ANALYSERS]



