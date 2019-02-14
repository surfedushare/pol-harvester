"""
Creates an index in elastic search.
We use the embedded elastic search config in the code.
See --help for options and arguments.
"""
import os

import requests
import click

import core

ANALYZERS = {
        'en': 'english',
        'nl': 'dutch'
    }

def get_index_config(lang):
    return {
        "settings" : {
            "index" : {
                "number_of_shards" : 1,
                "number_of_replicas" : 0
            }
        },
        'mappings': {
            '_doc': {
                'properties': {
                    'title': {
                        'type': 'text',
                        'analyzer': ANALYZERS[lang]
                    },
                    'text': {
                        'type': 'text',
                        'analyzer': ANALYZERS[lang]
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
    return {
        'title': doc['title'],
        'text': doc['text'],
        'url': doc['url'],
        'title_plain': doc['title'],
        'text_plain': doc['text'],
        'keywords': doc['arrangement_keywords'],
        'mime_type': doc['mime_type'],
        'conformed_mime_type': doc['conformed_mime_type'],
        'id': doc['id'],
        'arrangement_collection_name': doc['arrangement_collection_name']
    }

def create_index(url, auth, name, lang):
    """
    Creates an index with the supplied name, using the config
    """
    return requests.put(
        '{}/{}'.format(url, name),
        json=get_index_config(lang),
        auth=auth)

def delete_index(url, auth, name):
    """
    Deletes an index with the supplied name
    """
    return requests.delete('{}/{}'.format(url, name),
                           auth=auth).status_code == 200

def is_es_ok(url, auth):
    """
    Returns true if ES connection is ok
    """
    return requests.get('{}/{}'.format(url, '_cat/indices'), auth=auth).status_code == 200

def put_document(url, auth, name, document):
    """
    Uploads a document to elastic search index
    """
    doc_id_url = '{}/{}/_doc/{}'.format(url, name, document['id'])
    return requests.put(doc_id_url, auth=auth, json=to_es_document(document))

@click.command()
@click.argument('name')
@click.argument('credentials_file')
@click.argument('folder')
@click.argument('language')
def main(name, credentials_file, folder, language):
    logger = core.get_logger(__name__)
    url, auth = core.get_es_config(credentials_file)
    # test if it works
    if not is_es_ok(url, auth):
        logger.error('Credentials do not work for Elastic search')

    logger.info('Creating index')
    index_name = f'{name}-{language}'
    create_index(url, auth, index_name, language)
    for document in core.read_documents(os.path.join(folder, language)):
        response = put_document(url, auth, index_name, document)
        print(response.text)

if __name__ == '__main__':
    main()
