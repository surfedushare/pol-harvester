# Elasticsearch
To create an index in elasticsearch using data from Fako a few steps need to be taken.

The output from fako is a zip file (a freeze).
From the unzipped file "output/<collection>/with_text.json" is read.

That file is a collection of "arrangments".
These are then further flattened to "documents".
Then some cleaning is applied and the documents are split to "nl" and "en".
Last, a separate index is created for each language.

## Setup
You need to have elasticsearch credentials in a json file with the following structure.
{
  "username": "",
  "password": "",
  "url": "https://surfpol.sda.surf-hosted.nl"
}

## Read and flatten
Maps the unzipped output received from Fako to "documents".

    python read_freeze.py data/freeze3/output data/freeze3/elasticsearch

## Create index
Create an index given a directory.
We read the directory and expect to find a directory per language.
We attempt to create an index from each language found.

    python create_index.py index_name es-credentials.json clean.json

The index name with be suffixed with the language as in the folder.
The languages we support are "nl" and "en"

## Evaluate index
Evaluate an index given some metric (or omit for all).

    python eval.py queries.json index_name es-credentials.json 

## Digest evaluation

    bash digest_evaluation.sh index_name

# Managing the index

## List

    USER=$(cat es-credentials.json | jq '.username')
    PASS=$(cat es-credentials.json | jq '.password')
    curl --user $USER:$PASS -X GET "https://surfpol.sda.surf-hosted.nl/_cat/indices?v"

## Delete

    INDEX=haukur-test
    curl --user $USER:$PASS -X DELETE "https://surfpol.sda.surf-hosted.nl/$INDEX"
