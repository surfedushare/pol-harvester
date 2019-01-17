import logging
import hashlib

import spacy
from spacy_cld import LanguageDetector

from django.core.management.base import BaseCommand

from datagrowth.exceptions import DGResourceException
from pol_harvester.models import YouTubeDLResource, KaldiNLResource


nlp = spacy.load("nl_core_news_sm")
nlp.add_pipe(LanguageDetector())


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
            language = self.get_language_from_snippet(text)
        if title and not language:
            language = self.get_language_from_snippet(title)
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

    def get_language_from_snippet(self, snippet):
        doc = nlp(snippet)
        return doc._.languages[0] if doc._.languages else None

    def get_documents_from_kaldi(self, record):
        url = record.get("url", record.get("source"))  # edurep and sharekit scrapes name url slightly different
        title = record.get("title", None)
        if not title:
            return [self._create_document(None, record)]
        language = self.get_language_from_snippet(title) or record.get("language", None)
        if not language == "nl":
            return [self._create_document(None, record, language=language)]
        try:
            download = YouTubeDLResource(config={"fetch_only": True}).run(url)
        except DGResourceException:
            return [self._create_document(None, record)]
        _, file_paths = download.content
        if not len(file_paths):
            log.warning("Could not find download for: {}".format(url))
            return [self._create_document(None, record)]
        transcripts = []
        for file_path in file_paths:
            resource = KaldiNLResource(config={"fetch_only": True}).run(file_path)
            _, transcript = resource.content
            if transcript is None:
                log.warning("Could not find transcription for: {}".format(file_path))
            transcripts.append(self._create_document(transcript, record))
        return transcripts
