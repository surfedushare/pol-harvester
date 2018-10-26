import logging
import os
import json
from uuid import uuid4

from django.core.management.base import BaseCommand

from datagrowth.exceptions import DGResourceException
from pol_harvester.models import HttpTikaResource, YouTubeDLResource, KaldiNLResource
from edurep.models import EdurepFile


log = logging.getLogger(__name__)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-i', '--input', type=str, required=True)
        parser.add_argument('-o', '--output', type=str, required=True)

    def get_text_from_tika(self, record):
        text = None
        try:
            file = EdurepFile().get(record["source"])
            tika_hash = HttpTikaResource.hash_from_data({"file": file.body})
            tika_resource = HttpTikaResource.objects.get(data_hash=tika_hash)
            content_type, content = tika_resource.content
            text = content.get("text", None)
        except (DGResourceException, HttpTikaResource.DoesNotExist):
            pass
        return text

    def get_text_from_kaldi(self, record):
        download = YouTubeDLResource().run(record["source"])
        _, file_path = download.content
        if file_path is None:
            log.warning("Could not find download for: {}".format(record["source"]))
            return None
        transcription = KaldiNLResource().run(file_path)
        _, transcript = transcription.content
        return transcript

    def handle(self, *args, **options):

        with open(options["input"], "r") as json_file:
            records = json.load(json_file)

        base_dir = options["output"]
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)

        with_text = []

        for record in records:
            identifier = str(uuid4())
            text = self.get_text_from_tika(record) if not record["mime_type"].startswith("video") else \
                self.get_text_from_kaldi(record)
            output = {
                "id": identifier,
                "url": record["source"],
                "keywords": record["keywords"],
                "documents": [
                    {
                        "title": record["title"],
                        "url": record["source"],
                        "text": text,
                        "mime_type": record["mime_type"]
                    }
                ]
            }
            with open(os.path.join(base_dir, identifier + ".json"), "w") as record_file:
                json.dump(output, record_file)
            if text:
                with_text.append(output)

        with open(os.path.join(base_dir, "with_text.json"), "w") as record_file:
            json.dump(with_text, record_file, indent=4)
