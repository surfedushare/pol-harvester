import logging
import os
import json
from tqdm import tqdm

from pol_harvester.models import Arrangement
from pol_harvester.management.base import OutputCommand, FreezeCommand
from pol_harvester.utils.logging import log_header


out = logging.getLogger("freeze")


class Command(FreezeCommand, OutputCommand):

    def handle(self, *args, **options):

        log_header(out, "FREEZE LIBRARY 4 LEARNING", options)

        freeze, collection = self._get_or_create_context(options["freeze"], options["collection"])
        dumped = 0
        docs = 0

        with open(options["input"], "r") as json_file:
            records = json.load(json_file)

        for record in tqdm(records):
            documents = []
            for document in record.get("documents", []):
                documents.append(self._create_document(document["text"], document, pipeline={"raw": True}))
            dumped += 1
            docs += len(documents)

            arrangement = Arrangement.objects.create(
                freeze=freeze,
                collection=collection,
                schema={},
                referee="id",
                meta={
                    "id": record["id"],
                    "url": record["url"],
                    "keywords": record["keywords"]
                }
            )
            if len(documents):
                arrangement.add(documents, collection=collection)

        out.info("Dumped Arrangements: {}".format(dumped))
        out.info("Dumped Documents: {}".format(docs))
