import logging
import os
import json
from uuid import uuid4

from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage

from datagrowth.exceptions import DGResourceException
from pol_harvester.models import HttpTikaResource, YouTubeDLResource, KaldiNLResource
from edurep.models import EdurepFile
from ims.models import CommonCartridge


log = logging.getLogger(__name__)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-i', '--input', type=str, required=True)
        parser.add_argument('-o', '--output', type=str, required=True)

    def get_documents_from_tika(self, record):
        text = None
        try:
            file = EdurepFile().get(record["source"])
            tika_hash = HttpTikaResource.hash_from_data({"file": file.body})
            tika_resource = HttpTikaResource.objects.get(data_hash=tika_hash)
            content_type, content = tika_resource.content
            text = content.get("text", None)
        except (DGResourceException, HttpTikaResource.DoesNotExist):
            pass
        return [{
            "title": record["title"],
            "url": record["source"],
            "text": text,
            "mime_type": record["mime_type"]
        }]

    def get_documents_from_kaldi(self, record):
        download = YouTubeDLResource().run(record["source"])
        _, file_path = download.content
        if file_path is None:
            log.warning("Could not find download for: {}".format(record["source"]))
            return [{
                "title": record["title"],
                "url": record["source"],
                "text": None,
                "mime_type": record["mime_type"]
            }]
        transcription = KaldiNLResource().run(file_path)
        _, transcript = transcription.content
        if transcript is None:
            log.warning("Could not find transcription for: {}".format(record["source"]))
        return [{
            "title": record["title"],
            "url": record["source"],
            "text": transcript,
            "mime_type": record["mime_type"]
        }]

    def get_documents_from_imscp(self, record):
        documents = []
        try:
            archive_resource = EdurepFile().get(record["source"] + "?p=imscp")
            archive_file = archive_resource.body.replace(default_storage.base_location, "")
            archive = CommonCartridge.objects.get(file=archive_file)
            files = []
            resources = archive.get_resources().values()
            destination = archive.get_extract_destination()
            for resource in resources:
                if resource["content_type"] == "webcontent":
                    paths = [
                        os.path.join(default_storage.base_location, destination, file)
                        for file in resource["files"]
                    ]
                    files += paths
            for file in files:
                tika_hash = HttpTikaResource.hash_from_data({"file": file})
                tika_resource = HttpTikaResource.objects.get(data_hash=tika_hash)
                content_type, content = tika_resource.content
                text = content.get("text", None)
                url = record["source"] + file.replace(os.path.join(default_storage.base_location, destination), "")
                documents.append({
                    "title": content.get("title", [record["title"]])[0],
                    "url": url,
                    "text": text if text else None,
                    "mime_type": content.get("mime-type", None)
                })
        except (DGResourceException, HttpTikaResource.DoesNotExist, CommonCartridge.DoesNotExist):
            pass
        return documents

    def handle(self, *args, **options):

        with open(options["input"], "r") as json_file:
            records = json.load(json_file)

        base_dir = options["output"]
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)

        with_text = []

        for record in records:
            identifier = str(uuid4())
            if record["mime_type"].startswith("video"):
                documents = self.get_documents_from_kaldi(record)
            elif record["mime_type"] == "application/x-Wikiwijs-Arrangement":
                documents = self.get_documents_from_imscp(record)
            else:
                documents = self.get_documents_from_tika(record)

            output = {
                "id": identifier,
                "url": record["source"],
                "keywords": record["keywords"],
                "language": record["language"],
                "documents": documents
            }
            with open(os.path.join(base_dir, identifier + ".json"), "w") as record_file:
                json.dump(output, record_file)

            if any((doc for doc in documents if doc["text"] is not None)):
                with_text.append(output)

        with open(os.path.join(base_dir, "with_text.json"), "w") as record_file:
            json.dump(with_text, record_file, indent=4)
