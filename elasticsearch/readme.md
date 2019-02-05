
# Processing
To create an index in elastic search from data from Fako,
a few steps need to be taken.

The output from fako is a zip file, with some directory structure.
In that structure there are "objects", objects can contain many "documents".
The first step is to flatten the objects into documents.
Then we clean these docuemnts.
Lastly, we create indices based on languages.

## Map from raw
Maps the unzipped output received from Fako to "documents".
This is the flattening step.

    python map_from_raw.py input_directory flat.json

## Clean the documents
Cleans the documents by filtering out documents which do not conform.

    python clean_docs.py flat.json clean.json

## Create index
Creates an index (possibly multiple indices) in elastic search from documents.

    python create_index.py index_name es-credentials.json clean.json

Here we expect the es-credentials.json to be a json file with the following structure.

{
  "username": "",
  "password": "",
  "url": "https://surfpol.sda.surf-hosted.nl"
}

Multiple indices will be created per call, and the "index_name" is a prefix.
See the output of indices created.

## Evaluate index
Evaluate an index given some metric (or omit for all).

    python eval.py queries.json index_name es-credentials.json 

## Digest evaluation

    bash digest_evaluation.sh
# Managing the index

## List

    USER=
    PASS=
    curl --user $USER:$PASS -X GET "https://surfpol.sda.surf-hosted.nl/_cat/indices?v"

## Delete

    INDEX=haukur-test
    curl --user $USER:$PASS -X DELETE "https://surfpol.sda.surf-hosted.nl/$INDEX"
