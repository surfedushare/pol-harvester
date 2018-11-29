import logging
import os
import json
from uuid import uuid4
from tqdm import tqdm

from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage

import spacy
from spacy_cld import LanguageDetector

from datagrowth.exceptions import DGResourceException
from pol_harvester.models import HttpTikaResource, YouTubeDLResource, KaldiNLResource
from edurep.models import EdurepFile
from edurep.constants import TIKA_MIME_TYPES
from ims.models import CommonCartridge


log = logging.getLogger(__name__)


nlp = spacy.load("nl_core_news_sm")
nlp.add_pipe(LanguageDetector())


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-i', '--input', type=str, required=True)
        parser.add_argument('-o', '--output', type=str, required=True)

    def _create_document(self, text, meta, title=None, url=None, mime_type=None, language=None):
        title = title or meta.get("title", None)
        language = language or meta.get("language", None)
        if title and not language:
            language = self.get_language_from_snippet(title)
        return {
            "title": title,
            "language": language,
            "url": url or meta["source"],
            "text": text,
            "mime_type": mime_type or meta.get("mime_type", None)
        }

    def get_language_from_snippet(self, snippet):
        doc = nlp(snippet)
        return doc._.languages[0] if doc._.languages else None

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

    def get_documents_from_kaldi(self, record):
        try:
            download = YouTubeDLResource().run(record["source"])
        except DGResourceException:
            return [self._create_document(None, record)]
        _, file_paths = download.content
        if not len(file_paths):
            log.warning("Could not find download for: {}".format(record["source"]))
            return [self._create_document(None, record)]
        transcripts = []
        for file_path in file_paths:
            resource = KaldiNLResource().run(file_path)
            _, transcript = resource.content
            if transcript is None:
                log.warning("Could not find transcription for: {}".format(file_path))
            transcripts.append(self._create_document(transcript, record))
        return transcripts

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
            if record["mime_type"].startswith("video"):
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
