from datagrowth.resources import HttpResource

from pol_harvester.constants import PLAIN_TEXT_MIME_TYPES


class HttpTikaResource(HttpResource):
    URI_TEMPLATE = "https://analyzer.metadata.surfcatalog.nl/upload"
    FILE_DATA_KEYS = ["file"]

    def has_video(self):
        tika_content_type, data = self.content
        if data is None:
            return False
        text = data.get("text", "")
        content_type = data.get("content-type", "")
        if "leraar24.nl/api/video/" in text:
            return True
        if "video" in content_type:
            return True
        return any("video" in key for key in data.keys())

    def has_plain(self):
        tika_content_type, data = self.content
        if data is None:
            return False
        content_type = data.get("content-type", "")
        mime_type = data.get("mime-type", "")
        return content_type in PLAIN_TEXT_MIME_TYPES or mime_type in PLAIN_TEXT_MIME_TYPES

    def is_zip(self):
        tika_content_type, data = self.content
        if data is None:
            return False
        content_type = data.get("mime-type", "")
        return content_type == "application/zip"
