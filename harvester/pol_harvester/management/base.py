import logging
import hashlib

from django.conf import settings
from django.core.management.base import BaseCommand
from django.apps import apps

from datagrowth.exceptions import DGResourceException
from pol_harvester.models import YouTubeDLResource, Freeze, Collection
from pol_harvester.utils.language import get_language_from_snippet, get_kaldi_model_from_snippet


log = logging.getLogger(__name__)


class OutputCommand(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-i', '--input', type=str, required=True)
        parser.add_argument('-o', '--output', type=str, required=True)

    def _create_document(self, text, meta, title=None, url=None, mime_type=None):

        url = url or meta.get("url", meta.get("source"))  # edurep and sharekit scrapes name url slightly different
        hasher = hashlib.sha1()
        hasher.update(url.encode("utf-8"))
        identifier = hasher.hexdigest()

        text_language = get_language_from_snippet(text)
        title = title or meta.get("title", None)
        title_language = get_language_from_snippet(title)
        meta_language = meta.get("language", None)

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
            "mime_type": mime_type or meta.get("mime_type", None),
            "pipeline": {
                "harvest": settings.GIT_COMMIT
            }
        }

    def get_documents_from_kaldi(self, record):
        url = record.get("url", record.get("source"))  # edurep and sharekit scrapes name url slightly different
        kaldi_model = get_kaldi_model_from_snippet(
            record.get("title", None),
            default_language=record.get("language", None)
        )
        if kaldi_model is None:
            return [self._create_document(None, record)]
        try:
            download = YouTubeDLResource(config={"fetch_only": True}).run(url)
        except DGResourceException:
            return [self._create_document(None, record)]
        _, file_paths = download.content
        if not len(file_paths):
            log.warning("Could not find download for: {}".format(url))
            return [self._create_document(None, record)]
        Kaldi = apps.get_model(kaldi_model)
        transcripts = []
        for file_path in file_paths:
            resource = Kaldi(config={"fetch_only": True}).run(file_path)
            _, transcript = resource.content
            if transcript is None:
                log.warning("Could not find transcription for: {}".format(file_path))
            transcripts.append(self._create_document(transcript, record))
        return transcripts


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
