"""
Reads raw objects (from a directory) and maps them to documents (another directory).
Does no cleaning but takes care of mapping parent information to children.
"""
import os
import json
from itertools import chain

import click

# We define the repositories in code, so that we know what was ingested.
COLLECTION_NAMES = [
        'figshare',
        'hbovpk',
        'leraar24',
        'stimuleringsmaatregel',
        'wur',
        'wwmhbo'
        ]

def load_collection(root_directory, collection_name):
    """
    Loads a collection from disk
    """
    path = os.path.join(root_directory,
                        collection_name,
                        'with_text.json')
    with open(path) as stream:
        for item in json.load(stream):
            item['collection_name'] = collection_name
            yield item

def flatten_collections(items):
    """
    Flattens the collections to documents.
    Here we should preserve collection specific information/metadata.
    """
    for item in items:
        for doc_index, document in enumerate(item['documents']):
            # we do the editing inplace
            document['collection_name'] = item['collection_name']
            document['keywords'] = item.get('keywords', [])
            document['item_id'] = item['id']
            document['item_url'] = item['url']
            # TODO: Add specific collection enrichment here
            yield document

def write_documents(documents, file_name):
    """
    Writes all the documents to disk
    """
    with open(file_name, 'wt') as stream:
        json.dump(list(documents), stream, indent=2)


@click.command()
@click.argument('input_directory')
@click.argument('output_file')
def main(input_directory, output_file):
    items = chain.from_iterable([load_collection(input_directory, collection) 
                   for collection in COLLECTION_NAMES])
    documents = flatten_collections(items)
    write_documents(documents, output_file)

if __name__ == '__main__':
    main()
