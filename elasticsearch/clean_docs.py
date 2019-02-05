"""
Reads in a json file containing all the documents and filters them.
"""
import re
import json

import click

import core

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

def conform_mime_type(document):
    """
    Attempts to conform the type of document to a predefined list.
    """
    if 'mime_type' not in document:
        if 'content_type' in document:
            mime_type = document['content_type']
        else:
            # Try to infer mime type
            if 'youtube' in document['url']:
                mime_type = 'video'
            elif 'wurtv' in document['url']:
                mime_type = 'video'
            else:
                mime_type = 'unknown'
    else:
        mime_type = document['mime_type']
    if not mime_type:
        mime_type = 'unknown'

    # we are still not done, as the content type might be incorrect!
    if document['collection_name'] == 'leraar24' and 'html' in mime_type:
        mime_type = 'video'
    # or not 'standard'
    if 'html' in mime_type:
        mime_type = 'text/html'

    if 'video' in mime_type:
        mime_type = 'video'

    if 'image' in mime_type:
        mime_type = 'image'

    return HUMANIZED_MIME_TYPES[mime_type]

def clean_text(document):
    """
    Cleans the text in a document or sets it to an empty string
    """
    if 'text' in document and document['text']:
        text = re.sub(r'\s+', ' ', document['text'])
    else:
        text = ''
    # we don't do anything else at this time
    return text

@click.command()
@click.argument('input_file')
@click.argument('output_file')
def main(input_file, output_file):
    documents = core.read_documents(input_file)
    # we only keep 'nl' and 'en' languages
    documents = filter(lambda document: 'language' in document and
           (document['language'] == 'en' or document['language'] == 'nl'),
           documents)
    for document in documents:
        document['conformed_mime_type'] = conform_mime_type(document)
    # Only keep certain types of documents
    documents = filter(lambda document: ['video', 'word', 'powerp.', 'pdf'] 
            in document['conform_mime_type'], documents)
    # clean up the text
    for document in documents:
        document['text'] = clean_text(document)
    core.write_documents(documents, output_file, 'clean')

if __name__ == '__main__':
    main()
