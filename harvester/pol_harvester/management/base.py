import os
import hashlib
from urllib.parse import urlparse

from django.conf import settings
from django.core.management.base import BaseCommand

from pol_harvester.utils.language import get_language_from_snippet
from pol_harvester.constants import HIGHER_EDUCATION_LEVELS


class HarvesterCommand(BaseCommand):
    """
    This class adds some syntax sugar to make output of all commands similar
    """

    def error(self, message):
        self.stderr.write(self.style.ERROR(message))

    def warning(self, message):
        self.stderr.write(self.style.WARNING(message))

    def info(self, message):
        self.stdout.write(message)

    def success(self, message):
        self.stdout.write(self.style.SUCCESS(message))


class OutputCommand(HarvesterCommand):

    @staticmethod
    def _serialize_resource(resource=None):
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

    def get_file_type(self, mime_type=None, url=None):
        file_type = None
        if mime_type:
            file_type = settings.MIME_TYPE_TO_FILE_TYPE.get(mime_type, None)
        if not file_type and url:
            url = urlparse(url)
            file, extension = os.path.splitext(url.path)
            if extension and extension.lower() not in settings.EXTENSION_TO_FILE_TYPE:
                self.warning("Unknown extension: {}".format(extension))
            file_type = settings.EXTENSION_TO_FILE_TYPE.get(extension.lower(), "unknown")
        return file_type

    @staticmethod
    def get_lowest_educational_level(educational_levels):
        current_numeric_level = 3 if len(educational_levels) else -1
        for education_level in educational_levels:
            for higher_education_level, numeric_level in HIGHER_EDUCATION_LEVELS.items():
                if not education_level.startswith(higher_education_level):
                    continue
                # One of the seed's education levels matches a higher education level.
                # We re-assign current level and stop processing this education level,
                # as it shouldn't match multiple higher education levels
                current_numeric_level = min(current_numeric_level, numeric_level)
                break
            else:
                # No higher education level found inside current education level.
                # Dealing with an "other" means a lower education level than we're interested in.
                # So this seed has the lowest possible level. We're done processing this seed.
                current_numeric_level = 0
                break
        return current_numeric_level

    def _create_document(self, text, meta, title=None, url=None, mime_type=None, file_type=None, pipeline=None,
                         hash_postfix=None):

        url = url or meta.get("url")
        mime_type = mime_type or meta.get("mime_type", None)
        file_type = file_type or self.get_file_type(mime_type, url)

        hash_postfix = hash_postfix if hash_postfix is not None else mime_type
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
            "external_id": meta["external_id"],
            "title": title,
            "language": {
                "metadata": meta_language,
                "from_text": text_language,
                "from_title": title_language
            },
            "url": url,
            "text": text,
            "file_type": file_type,
            "mime_type": mime_type,
            "author": meta.get("author", []),
            "description": meta.get("description", None),
            "copyright": meta.get("copyright", None),
            "publisher_date": meta.get("publisher_date", None),
            "disciplines": meta.get("disciplines", []),
            "educational_levels": meta.get("educational_levels", []),
            "lowest_educational_level": self.get_lowest_educational_level(meta.get("lom_educational_levels", [])),
            "suggest": title,
            "pipeline": pipeline
        }
