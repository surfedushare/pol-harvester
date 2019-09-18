from datagrowth.resources import HttpResource


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

    def has_html(self):
        tika_content_type, data = self.content
        if data is None:
            return False
        content_type = data.get("content-type", "")
        return "html" in content_type

    def is_zip(self):
        tika_content_type, data = self.content
        if data is None:
            return False
        content_type = data.get("content-type", "")
        return content_type == "application/zip"
