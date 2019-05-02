# Elasticsearch
To create an index in elasticsearch using data from Fako a few steps need to be taken.

The output from fako is a zip file (a freeze).
From the unzipped file "output/<collection>/with_text.json" is read.

That file is a collection of "arrangments".
These are then further flattened to "documents".
Then the documents are split to "nl" and "en".
Last, a separate index is created for each language.

## Setup
You need to have elasticsearch credentials in a json file with the following structure.
{
  "username": "",
  "password": "",
  "url": "https://surfpol.sda.surf-hosted.nl"
  "host": "surfpol.sda.surf-hosted.nl"
}

## Create index
Create an index given a directory.
We attempt to create an index from each language found.

    python create_index.py freeze3 es-credentials.json data/freeze3/elasticsearch

The index name with be suffixed with the language as in the folder.
The languages we support are "nl" and "en"

## Evaluate index
Evaluate an index given some metric (or omit for all).

    python eval.py queries-nl.json freeze3-nl es-credentials.json data/freeze3/evaluation

