import json
import subprocess
import os
import glob
import logging

GIT_MARKER = None
COLLECTION_NAMES = [
        'figshare',
        'hbovpk',
        'leraar24',
        'stimuleringsmaatregel',
        'wur',
        'wwmhbo'
    ]


def get_logger(name):
    logging.basicConfig(format='[%(asctime)-15s][%(levelname)-7s] %(message)s',
            level=logging.DEBUG)
    logger = logging.getLogger(name)
    return logger


def get_es_config(file_path):
    """
    Reads a json file containing the elastic search credentials and url.
    The file is expected to have 'url', 'username' and 'password' keys
    """
    with open(file_path) as stream:
        credentials = json.load(stream)
    return (credentials['url'],
            (credentials['username'], credentials['password']))


def read_documents(folder):
    documents = glob.glob(f'{folder}/*.json')
    for document in documents:
        with open(document, 'rt') as stream:
            yield json.load(stream)


def read_raw_documents(directory):
    """
    Returns an iterable of documents
    """
    for collection in COLLECTION_NAMES:
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

