import json
import subprocess

def read_documents(file_path):
    with open(file_path, 'rt') as stream:
        return json.load(stream)

def _get_git_marker():
    return subprocess.check_output(['git', 'describe', '--always']).strip()

def write_documents(documents, file_path, stage):
    for document in documents:
        if 'pipeline' not in document:
            document['pipeline'] = {}
        document['pipeline'][stage] = _get_git_marker()
    with open(file_path, 'wt') as stream:
        json.dump(documents, stream)
