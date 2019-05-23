import json
import os
from collections import defaultdict

from elasticsearch.helpers import streaming_bulk
from elasticsearch import Elasticsearch

from django.core.management.base import BaseCommand
from pol_harvester.models import Arrangement
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


def to_dict(arrangement):
    keys = arrangement.meta.keys()
    for dictionary in arrangement.content:
        # we add all the keys with a prefix, except for the 'pipeline'
        for key in keys:
            if key == 'documents':
                continue
            if key == 'pipeline':
                dictionary[key] = arrangement.meta[key]
            else:
                dictionary[f'arrangement_{key}'] = arrangement.meta[key]
        dictionary["arrangement_collection_name"] = arrangement.collection.name
        yield dictionary


def to_es_document(dictionary):
    """
    Returns a correctly formatted elasticsearch document from a given document.
    This needs to correspond correctly with the properties defined in the
    index.
    """
    return {
        'title': dictionary['title'],
        'text': dictionary['text'],
        'url': dictionary['url'],
        'title_plain': dictionary['title'],
        'text_plain': dictionary['text'],
        'keywords': dictionary['arrangement_keywords'],
        'humanized_mime_type': HUMANIZED_MIME_TYPES.get(dictionary['mime_type'],
                                                        'unknown'),
        'mime_type': dictionary['mime_type'],
        '_id': dictionary['id'],
        'arrangement_collection_name': dictionary['arrangement_collection_name']
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

        index_name = "freeze-alpha-test-02"
        credentials_file = "../es_credentials.json"
        recreate = True

        freeze_name = "alpha"
        arrangements = Arrangement.objects.filter(freeze__name=freeze_name)
        print(f"freeze { freeze_name } arrangement count: {len(arrangements)}")

        lang_doc = []
        for arrangement in arrangements:
            for dictionary in to_dict(arrangement):
                lang = get_language(dictionary)
                lang_doc.append((lang, dictionary,))

        lang_doc_dict = defaultdict(list)
        # create a list so we can report counts
        for lang, doc in lang_doc:
            lang_doc_dict[lang].append(doc)
        for lang in lang_doc_dict.keys():
            log.info(f'{lang}:{len(lang_doc_dict[lang])}')

        es = get_es_client(credentials_file)
        [create_index(es, index_name, lang, lang_doc_dict[lang], recreate)
         for lang in lang_doc_dict.keys() if lang in ANALYSERS]



