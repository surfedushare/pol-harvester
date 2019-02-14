"""
Creates an index in elastic search.
We use the embedded elastic search config in the code.
See --help for options and arguments.
"""
import os

import click
from elasticsearch.helpers import streaming_bulk

import util

ANALYSERS = {
    'en': 'english',
    'nl': 'dutch'
}


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
                    'conformed_mime_type': {'type': 'text'},
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
        'keywords': doc['arrangement_keywords'],
        'mime_type': doc['mime_type'],
        'conformed_mime_type': doc['conformed_mime_type'],
        '_id': doc['id'],
        'arrangement_collection_name': doc['arrangement_collection_name']
    }


def create_index(client, name, config):
    """
    Creates an index with the supplied name, using the config.
    """
    return client.indices.create(
        index=name,
        body=config)


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
            print(result)


def read_languages(folder):
    """
    Returns the languages defined the folder structure.
    """
    return [entity for entity in os.listdir(folder)]


@click.command()
@click.argument('name')
@click.argument('credentials_file')
@click.argument('folder')
@click.option('--recreate', type=bool, default=True)
def main(name, credentials_file, folder, recreate):
    logger = util.get_logger(__name__)

    languages = read_languages(folder)
    for language in languages:
        index_name = f'{name}-{language}'
        logger.info(f'Creating index: {index_name}')

        es = util.get_es_client(credentials_file)

        config = get_index_config(language)
        if es.indices.exists(index_name):
            if recreate:
                es.indices.delete(index_name)
            else:
                raise Exception(f"Index {index_name} already exists.")

        create_index(es, index_name, config)
        bulk_insert_documents(es, index_name, util.read_documents(
            os.path.join(folder, language)))


if __name__ == '__main__':
    main()
