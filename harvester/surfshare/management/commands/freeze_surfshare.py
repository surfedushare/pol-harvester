import logging
import os
import json
from urlobject import URLObject
from tqdm import tqdm

from pol_harvester.management.base import OutputCommand, FreezeCommand
from pol_harvester.models import Arrangement
from pol_harvester.utils.logging import log_header
from surfshare.constants import VIDEO_DOMAINS


out = logging.getLogger("freeze")


class Command(FreezeCommand, OutputCommand):

    def handle(self, *args, **options):

        log_header(out, "FREEZE SURFSHARE", options)

        freeze, collection = self._get_or_create_context(options["freeze"], options["collection"])

        for path, dirs, files in os.walk(options["input"]):

            copied = 0
            videos = 0
            docs = 0
            dumped = 0

            for file in tqdm(files):
                with open(os.path.join(path, file), "r") as json_file:
                    data = json.load(json_file)
                if "original_article" in data:
                    del data["original_article"]
                documents = []
                for document in data.get("documents", []):
                    content_type = document.get("content-type", None)
                    document["mime_type"] = content_type
                    if content_type:
                        del document["content-type"]
                    if not document.get("title", None):
                        document["title"] = data.get("title", None)
                    url = URLObject(document["url"])
                    if url.hostname in VIDEO_DOMAINS:
                        vids = self.get_documents_from_kaldi(document)
                        videos += len(vids)
                        documents += vids
                    else:
                        copied += 1
                        documents.append(self._create_document(document["text"], document, pipeline={"raw": True}))
                dumped += 1
                docs += len(documents)

                arrangement = Arrangement.objects.create(
                    freeze=freeze,
                    collection=collection,
                    schema={},
                    referee="id",
                    meta={
                        "id": data["id"],
                        "url": data["url"],
                        "keywords": data["keywords"]
                    }
                )
                if len(documents):
                    arrangement.add(documents, collection=collection)

            out.info("Copied from raw data during dump: {}".format(copied))
            out.info("Transcribed videos: {}".format(videos))
            out.info("Dumped Arrangements: {}".format(dumped))
            out.info("Dumped Documents: {}".format(docs))
