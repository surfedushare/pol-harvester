import logging
import json
from uuid import uuid4
from tqdm import tqdm
from urlobject import URLObject

from pol_harvester.models import Arrangement
from pol_harvester.management.base import OutputCommand, FreezeCommand
from pol_harvester.utils.logging import log_header
from edurep.constants import TIKA_MIME_TYPES, VIDEO_DOMAINS


out = logging.getLogger("freeze")


class Command(FreezeCommand, OutputCommand):

    def handle(self, *args, **options):

        log_header(out, "FREEZE EDUREP", options)

        freeze, collection = self._get_or_create_context(options["freeze"], options["collection"])
        skipped = 0
        dumped = 0
        docs = 0

        with open(options["input"], "r") as json_file:
            records = json.load(json_file)

        for record in tqdm(records):
            identifier = str(uuid4())
            url = URLObject(record["url"])
            if url.hostname in VIDEO_DOMAINS:
                record["source"] = str(url)
                documents = self.get_documents_from_kaldi(record)
            elif record["mime_type"] == "application/x-Wikiwijs-Arrangement":
                documents = self.get_documents_from_imscp(record)
            elif record["mime_type"] in TIKA_MIME_TYPES:
                documents = self.get_documents_from_tika(record)
            else:
                skipped += 1
                continue
            dumped += 1
            docs += len(documents)

            arrangement = Arrangement.objects.create(
                freeze=freeze,
                collection=collection,
                schema={},
                referee="id",
                meta={
                    "id": identifier,
                    "url": record["url"],
                    "keywords": record["keywords"]
                }
            )
            if len(documents):
                arrangement.add(documents, collection=collection)

        out.info("Skipped URL's during dump: {}".format(skipped))
        out.info("Dumped Arrangements: {}".format(dumped))
        out.info("Dumped Documents: {}".format(docs))
