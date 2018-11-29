import logging
import os
import json
from uuid import uuid4
from tqdm import tqdm
from urlobject import URLObject

from django.core.files.storage import default_storage

from datagrowth.exceptions import DGResourceException
from pol_harvester.models import HttpTikaResource
from pol_harvester.management.base import DumpCommand
from edurep.models import EdurepFile
from edurep.constants import TIKA_MIME_TYPES, VIDEO_DOMAINS
from ims.models import CommonCartridge


log = logging.getLogger(__name__)


class Command(DumpCommand):

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
        return [
            self._create_document(text, record)
        ]

    def get_documents_from_imscp(self, record):
        del record["mime_type"]  # because this *never* makes sense for the package documents inside
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
                title = content.get("title", [None])[0]
                documents.append(
                    self._create_document(
                        text if text else None,
                        record,
                        title=title,
                        url=url,
                        mime_type=content.get("mime-type", None)
                    ),

                )
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

        for record in tqdm(records):
            identifier = str(uuid4())
            if URLObject(record["source"]).hostname in VIDEO_DOMAINS:
                documents = self.get_documents_from_kaldi(record)
            elif record["mime_type"] == "application/x-Wikiwijs-Arrangement":
                documents = self.get_documents_from_imscp(record)
            elif record["mime_type"] in TIKA_MIME_TYPES:
                documents = self.get_documents_from_tika(record)
            else:
                continue

            output = {
                "id": identifier,
                "url": record["source"],
                "keywords": record["keywords"],
                "documents": documents
            }
            with open(os.path.join(base_dir, identifier + ".json"), "w") as record_file:
                json.dump(output, record_file)

            if any((doc for doc in documents if doc["text"] is not None)):
                with_text.append(output)

        with open(os.path.join(base_dir, "with_text.json"), "w") as record_file:
            json.dump(with_text, record_file, indent=4)
