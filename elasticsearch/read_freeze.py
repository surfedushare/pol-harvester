#!/usr/bin/env python3
"""
Reads in a json file containing all the documents and filters them.
"""
import os
import re
from itertools import tee

import click

import util

LANGUAGES = ['en', 'nl']
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


def get_mime_type(document):
    """
    Attempts to conform the type of document to a predefined list.
    """
    mime_type = document.get('mime_type', None)
    if mime_type is None:
        mime_type = document.get('arrangement_mime_type', None)
    if mime_type is None:
        mime_type = document.get('content_type', None)
    if mime_type is None:
        mime_type = document.get('arrangement_content_type', None)
    if mime_type is None:
        # Try to infer mime type
        if 'youtube' in document['url']:
            mime_type = 'video'
        elif 'wurtv' in document['url']:
            mime_type = 'video'
        else:
            mime_type = 'unknown'

    # we are still not done, as the content type might be incorrect!
    if document['arrangement_collection_name'] == 'leraar24' and 'html' in mime_type:
        mime_type = 'video'
    # or not 'standard'
    if 'html' in mime_type:
        mime_type = 'text/html'

    if 'video' in mime_type:
        mime_type = 'video'

    if 'image' in mime_type:
        mime_type = 'image'

    return HUMANIZED_MIME_TYPES[mime_type]


def get_text(document):
    """
    Cleans the text in a document or sets it to an empty string
    """
    if 'text' in document and document['text']:
        text = re.sub(r'\s+', ' ', document['text'])
    else:
        text = ''
    # we don't do anything else at this time
    return text


def process_documents(documents):
    for document in documents:
        document['text'] = get_text(document)
        document['conformed_mime_type'] = get_mime_type(document)

        # Only keep certain types of documents
        for mime_type in ['video', 'word', 'powerp.', 'pdf']:
            if mime_type not in document['conformed_mime_type']:
                continue

        # we only keep 'nl' and 'en' languages
        if document['language'] not in ['nl', 'en']:
            continue

        yield document


@click.command()
@click.argument('input_directory')
@click.argument('output_directory')
def main(input_directory, output_directory):
    logger = util.get_logger(__name__)

    logger.info(f'Reading collections')
    documents = util.read_raw_documents(input_directory)

    logger.info(f'Cleaning fields')

    for documents_iterator, lang in zip(
            tee(process_documents(documents),
                len(LANGUAGES)),
            LANGUAGES):
        logger.info(f'Writing files for {lang}')
        util.write_documents(
            (doc for doc in documents_iterator if doc['language'] == lang),
            os.path.join(output_directory, lang),
            'clean')


if __name__ == '__main__':
    main()
