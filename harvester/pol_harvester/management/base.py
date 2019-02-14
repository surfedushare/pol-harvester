import logging
import hashlib

from django.core.management.base import BaseCommand
from django.apps import apps

from datagrowth.exceptions import DGResourceException
from pol_harvester.models import YouTubeDLResource
from pol_harvester.utils.language import get_language_from_snippet, get_kaldi_model_from_snippet


log = logging.getLogger(__name__)


class DumpCommand(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-i', '--input', type=str, required=True)
        parser.add_argument('-o', '--output', type=str, required=True)

    def _create_document(self, text, meta, title=None, url=None, mime_type=None, language=None):

        url = url or meta.get("url", meta.get("source"))  # edurep and sharekit scrapes name url slightly different
        hasher = hashlib.sha1()
        hasher.update(url.encode("utf-8"))
        identifier = hasher.hexdigest()
        title = title or meta.get("title", None)
        if text and not language:
            language = get_language_from_snippet(text)
        if title and not language:
            language = get_language_from_snippet(title)
        if not language:
            language = meta.get("language", "unknown")

        return {
            "id": identifier,
            "title": title,
            "language": language,
            "url": url,
            "text": text,
            "mime_type": mime_type or meta.get("mime_type", None)
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