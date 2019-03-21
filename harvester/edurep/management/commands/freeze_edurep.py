import logging
import os
import json
from uuid import uuid4
from tqdm import tqdm
from urlobject import URLObject

from django.core.files.storage import default_storage

from datagrowth.exceptions import DGResourceException
from pol_harvester.models import HttpTikaResource, Arrangement
from pol_harvester.management.base import DumpCommand, FreezeCommand
from edurep.models import EdurepFile
from edurep.constants import TIKA_MIME_TYPES, VIDEO_DOMAINS
from ims.models import CommonCartridge


log = logging.getLogger(__name__)


class Command(FreezeCommand, DumpCommand):

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
            archive = CommonCartridge.objects.get(file=archive_resource.body)
            files = []
            resources = archive.get_resources().values()
            destination = archive.get_extract_destination()
            destination = destination.replace(default_storage.base_location, "").lstrip(os.sep)
            for resource in resources:
                if resource["content_type"] == "webcontent":
                    paths = [
                        os.path.join(destination, file)
                        for file in resource["files"]
                    ]
                    files += paths
            for file in files:
                tika_hash = HttpTikaResource.hash_from_data({"file": file})
                tika_resource = HttpTikaResource.objects.get(data_hash=tika_hash)
                content_type, content = tika_resource.content
                text = content.get("text", None)
                url = record["source"] + file.replace(destination, "")
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

        freeze, collection = self._get_or_create_context(options["freeze"], options["collection"])
        skipped = 0

        with open(options["input"], "r") as json_file:
            records = json.load(json_file)

        for record in tqdm(records):
            identifier = str(uuid4())
            url = URLObject(record["source"])
            if url.hostname in VIDEO_DOMAINS:
                if "youtube.com" in url.hostname:
                    url = url.del_query_param('list')
                    url = url.del_query_param('index')
                record["source"] = str(url)
                documents = self.get_documents_from_kaldi(record)
            elif record["mime_type"] == "application/x-Wikiwijs-Arrangement":
                documents = self.get_documents_from_imscp(record)
            elif record["mime_type"] in TIKA_MIME_TYPES:
                documents = self.get_documents_from_tika(record)
            else:
                skipped += 1
                continue

            arrangement = Arrangement.objects.create(
                freeze=freeze,
                collection=collection,
                schema={},
                referee="id",
                meta={
                    "id": identifier,
                    "url": record["source"],
                    "keywords": record["keywords"]
                }
            )
            if len(documents):
                arrangement.add(documents, collection=collection)

        print("Completed with {} skipped".format(skipped))
