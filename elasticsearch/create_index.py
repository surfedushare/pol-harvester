"""
Creates an index in elastic search.
We use the embedded elastic search config in the code.
See --help for options and arguments.
"""
import json
import logging
import glob
import os

import requests
import click

import core


def get_index_config():
    return {
        'mappings': {
            '_doc': {
                'properties': {
                    'title': {'type': 'text'},
                    'text': {
                        'type': 'object',
                        'properties': {
                            'en': {
                                'type': 'text',
                                'analyzer': 'english'
                            },
                            'nl': {
                                'type': 'text',
                                'analyzer': 'dutch'
                            }
                        }
                    },
                    'url': {'type': 'text'},
                    'keywords': {'type': 'text'},
                    'mime_type': {'type': 'text'},
                    'humanized_mime_type': {'type': 'text'},
                    'item_id': {'type': 'text'},
                    'item_url': {'type': 'text'},
                    'collection_name': {'type': 'text'}
                }
            }
        }
    }

def create_index(url, auth, name):
    """
    Creates an index with the supplied name, using the config
    """
    return requests.put(
        '{}/{}'.format(url, name),
        json=get_index_config(),
        auth=auth).status_code == 201

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
    requests.put(doc_id_url, auth=auth, json=document)

@click.command()
@click.argument('name')
@click.argument('credentials_file')
@click.argument('documents_file')
def main(name, credentials_file, documents_file):
    logger = logging.getLogger(__name__)
    url, auth = core.get_es_config(credentials_file)
    # test if it works
    if not is_es_ok(url, auth):
        logger.error('Credentials do not work for Elastic search')

    logger.info('Creating index')
    create_index(url, auth, name)
    for document in core.read_documents(documents_file):
        put_document(url, auth, name, document)


if __name__ == '__main__':
    main()
