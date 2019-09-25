import logging
import os
import hashlib

from django.conf import settings
from django.core.management.base import BaseCommand
from django.apps import apps
from django.core.files.storage import default_storage

from datagrowth.exceptions import DGResourceException
from datagrowth import settings as datagrowth_settings
from pol_harvester.models import YouTubeDLResource, Freeze, Collection, HttpTikaResource
from pol_harvester.utils.language import get_language_from_snippet, get_kaldi_model_from_snippet
from edurep.models import EdurepFile
from ims.models import CommonCartridge


log = logging.getLogger(__name__)


class OutputCommand(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-i', '--input', type=str, required=True)
        parser.add_argument('-o', '--output', type=str, required=True)

    @staticmethod
    def _serialize_resource(resource):
        if resource is None:
            return {
                "success": False,
                "resource": None
            }
        return {
            "success": resource.success,
            "resource": ["{}.{}".format(resource._meta.app_label, resource._meta.model_name), resource.id]
        }

    @staticmethod
    def get_hash_from_url(url, postfix=None):
        hasher = hashlib.sha1()
        payload = url + postfix if postfix else url
        hasher.update(payload.encode("utf-8"))
        return hasher.hexdigest()

    def _create_document(self, text, meta, title=None, url=None, mime_type=None, pipeline=None, hash_postfix=None):

        url = url or meta.get("url")
        mime_type = mime_type or meta.get("mime_type", None),
        hash_postfix = hash_postfix or mime_type
        identifier = self.get_hash_from_url(url, postfix=hash_postfix)

        text_language = get_language_from_snippet(text)
        title = title or meta.get("title", None)
        title_language = get_language_from_snippet(title)
        meta_language = meta.get("language", None)

        pipeline = pipeline or {}
        assert isinstance(pipeline, dict), "Pipeline should be a dictionary got {} instead".format(type(pipeline))
        pipeline["harvest"] = settings.GIT_COMMIT

        return {
            "id": identifier,
            "title": title,
            "language": {
                "metadata": meta_language,
                "from_text": text_language,
                "from_title": title_language
            },
            "url": url,
            "text": text,
            "mime_type": mime_type,
            "pipeline": pipeline
        }

    def get_documents_from_kaldi(self, record):
        url = record.get("url")
        pipeline = {
            "download": self._serialize_resource(None),
            "kaldi": self._serialize_resource(None)
        }
        kaldi_model = get_kaldi_model_from_snippet(
            record.get("title", None),
            default_language=record.get("language", None)
        )
        if kaldi_model is None:
            return [self._create_document(None, record, pipeline=pipeline)]
        try:
            download = YouTubeDLResource(config={"fetch_only": True}).run(url)
            pipeline["download"] = self._serialize_resource(download)
        except DGResourceException:
            return [self._create_document(None, record, pipeline=pipeline)]
        _, file_paths = download.content
        if not len(file_paths):
            log.warning("Could not find download for: {}".format(url))
            return [self._create_document(None, record, pipeline=pipeline)]
        Kaldi = apps.get_model(kaldi_model)
        transcripts = []
        file_path = file_paths[0]
        resource = Kaldi(config={"fetch_only": True}).run(file_path)
        pipeline["kaldi"] = self._serialize_resource(resource)
        _, transcript = resource.content
        if transcript is None:
            log.warning("Could not find transcription for: {}".format(file_path))
        transcripts.append(self._create_document(transcript, record, pipeline=pipeline))
        return transcripts

    def get_documents_from_tika(self, record):
        text = None
        file_resource = None
        tika_resource = None
        try:
            file_resource = EdurepFile().get(record["url"])
            tika_hash = HttpTikaResource.hash_from_data({"file": file_resource.body})
            tika_resource = HttpTikaResource.objects.get(data_hash=tika_hash)
            content_type, content = tika_resource.content
            text = content.get("text", None)
        except (DGResourceException, HttpTikaResource.DoesNotExist):
            pass
        return [
            self._create_document(text, record, pipeline={
                "download": self._serialize_resource(file_resource),
                "tika": self._serialize_resource(tika_resource)
            })
        ]

    def get_documents_from_imscp(self, record):
        del record["mime_type"]  # because this *never* makes sense for the package documents inside
        documents = []
        try:
            archive_resource = EdurepFile().get(record["url"] + "?p=imscp")
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
                tika_hash = HttpTikaResource.hash_from_data({
                    "file": os.path.join(datagrowth_settings.DATAGROWTH_MEDIA_ROOT, file)
                })
                tika_resource = HttpTikaResource.objects.get(data_hash=tika_hash)
                content_type, content = tika_resource.content
                if content is None:
                    content = {}
                text = content.get("text", None)
                title = content.get("title", [None])[0]
                url = record["url"] + file.replace(destination, "")
                documents.append(
                    self._create_document(
                        text if text else None,
                        record,
                        title=title,
                        url=url,
                        mime_type=content.get("mime-type", None),
                        pipeline={
                            "download": self._serialize_resource(archive_resource),
                            "package": self._serialize_resource(archive),
                            "tika": self._serialize_resource(tika_resource)
                        }
                    )
                )
        except (DGResourceException, HttpTikaResource.DoesNotExist, CommonCartridge.DoesNotExist):
            pass
        return documents


class FreezeCommand(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-i', '--input', type=str, required=True)
        parser.add_argument('-f', '--freeze', type=str, required=True)
        parser.add_argument('-c', '--collection', type=str, required=True)

    def _get_or_create_context(self, freeze_name, collection_name):
        freeze, created = Freeze.objects.get_or_create(name=freeze_name)
        freeze.referee = "id"
        freeze.save()
        if created:
            log.info("Created freeze " + freeze_name)
        else:
            log.info("Adding to freeze " + freeze_name)
        collection, created = Collection.objects.get_or_create(name=collection_name, freeze=freeze)
        collection.referee = "id"
        collection.save()
        if created:
            log.info("Created collection " + collection_name)
        else:
            log.info("Adding to collection " + collection_name)
        return freeze, collection
