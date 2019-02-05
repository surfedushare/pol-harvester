import json
import subprocess

GIT_MARKER = None

def get_es_config(file_path):
    """
    Reads a json file containing the elastic search credentials and url.
    The file is expected to have 'url', 'username' and 'password' keys
    """
    with open(file_path) as stream:
        credentials = json.load(stream)
    return (credentials['url'],
            (credentials['username'], credentials['password']))

def read_documents(file_path):
    with open(file_path, 'rt') as stream:
        return json.load(stream)

def _get_git_marker():
    global GIT_MARKER
    if not GIT_MARKER:
        GIT_MARKER = subprocess.check_output(['git', 'describe', '--always']).decode('utf-8').strip()
    return GIT_MARKER

def write_documents(documents, file_path, stage):
    for document in documents:
        if 'pipeline' not in document:
            document['pipeline'] = {}
        document['pipeline'][stage] = _get_git_marker()
    with open(file_path, 'wt') as stream:
        json.dump(documents, stream)
