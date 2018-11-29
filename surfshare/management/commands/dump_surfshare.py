import logging
import os
import json
from urlobject import URLObject

from django.core.management.base import BaseCommand

from datagrowth.exceptions import DGResourceException
from pol_harvester.models import YouTubeDLResource, KaldiNLResource
from surfshare.constants import VIDEO_DOMAINS


log = logging.getLogger(__name__)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-i', '--input', type=str, required=True)
        parser.add_argument('-o', '--output', type=str, required=True)

    def get_documents_from_kaldi(self, document):
        try:
            download = YouTubeDLResource().run(document["url"])
        except DGResourceException:
            return [{
                "title": document["title"],
                "url": document["url"],
                "text": None,
                "mime_type": document["content-type"]
            }]
        _, file_paths = download.content
        if not len(file_paths):
            log.warning("Could not find download for: {}".format(document["url"]))
            return [{
                "title": document["title"],
                "url": document["url"],
                "text": None,
                "mime_type": document["content-type"]
            }]
        transcripts = []
        for file_path in file_paths:
            resource = KaldiNLResource().run(file_path)
            _, transcript = resource.content
            if transcript is None:
                log.warning("Could not find transcription for: {}".format(file_path))
            transcripts.append({
                "title": document["title"],
                "url": document["url"],
                "text": transcript,
                "mime_type": document["content-type"]
            })
        return transcripts

    def handle(self, *args, **options):

        base_dir = options["output"]
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)

        with_text = []

        for path, dirs, files in os.walk(options["input"]):
            for file in files:
                with open(os.path.join(path, file), "r") as json_file:
                    data = json.load(json_file)
                documents = []
                for document in data.get("documents", []):
                    if URLObject(document["url"]).hostname in VIDEO_DOMAINS:
                        documents += self.get_documents_from_kaldi(document)
                    else:
                        document["mime_type"] = document["content-type"]
                        del document["content-type"]
                        documents.append(document)
                data["documents"] = documents

                if any((doc for doc in documents if doc["text"] is not None)):
                    with_text.append(data)

                with open(os.path.join(base_dir, file), "w") as json_file:
                    json.dump(data, json_file)

        with open(os.path.join(base_dir, "with_text.json"), "w") as record_file:
            json.dump(with_text, record_file, indent=4)
