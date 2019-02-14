#!/usr/bin/env python3
"""
This module contains utility functions.
"""
import json
import subprocess
import os
import glob
import logging
from elasticsearch import Elasticsearch

GIT_MARKER = None


def get_logger(name):
    """
    Returns a logger with unified format and level set
    """
    logging.basicConfig(format='[%(asctime)-15s][%(levelname)-7s] %(message)s',
                        level=logging.INFO)
    logger = logging.getLogger(name)
    return logger


def get_indices(es_client, index_name):
    return es_client.cat.indices(index_name)

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


def read_documents(folder):
    """
    Returns a generator which yields all json files in a folder
    """
    documents = glob.glob(f'{folder}/*.json')
    for document in documents:
        with open(document, 'rt') as stream:
            yield json.load(stream)


def read_raw_documents(directory):
    """
    Returns an iterable of documents
    """
    collections = os.listdir(directory)
    for collection in collections:
        collection_path = os.path.join(directory, collection)
        # We only use the "with_text.json"
        with open(f'{collection_path}/with_text.json', 'rt') as stream:
            for arrangement in json.load(stream):
                arrangement['collection_name'] = collection
                for document in to_document(arrangement):
                    yield document


def to_document(arrangement):
    keys = arrangement.keys()
    for document in arrangement['documents']:
        # we add all the remaining keys
        for key in keys:
            if key not in document and key not in 'documents':
                document[f'arrangement_{key}'] = arrangement[key]
        yield document


def _get_git_marker():
    """
    Returns the git hash or tag of the current head
    """
    global GIT_MARKER
    if not GIT_MARKER:
        GIT_MARKER = subprocess.check_output(['git', 'describe', '--always']) \
            .decode('utf-8').strip()
    return GIT_MARKER


def write_documents(documents, folder, stage):
    """
    Writes all the documents to a folder.
    The documents have the name id.json
    """
    # We allow writing to existing folders, mostlikely overwriting.
    os.makedirs(folder, exist_ok=True)
    for document in documents:
        if 'pipeline' not in document:
            document['pipeline'] = {}
        document['pipeline'][stage] = _get_git_marker()
        file_name = os.path.join(folder, f'{document["id"]}.json')
        with open(file_name, 'w+t') as stream:
            json.dump(document, stream)
