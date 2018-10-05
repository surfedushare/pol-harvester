import os
from datetime import datetime
from urlobject import URLObject
from io import BytesIO

from django.conf import settings
from django.core.files.storage import default_storage
from django.core.exceptions import ValidationError
from django.core.files import File

from datagrowth.resources.http.generic import HttpResource


class HttpFileResource(HttpResource):

    GET_SCHEMA = {
        "args": {
            "type": "array",
            "items": [
                {
                    "type": "string",
                    "pattern": "^http"
                },
                {
                    "type": "string"
                }
            ],
            "minItems": 1,
            "additionalItems": False
        }
    }

    def variables(self, *args):
        args = args or self.request.get("args")
        return {
            "url": args[0]
        }

    def _send(self):
        if self.request["cancel"]:
            return
        super()._send()

    def _create_request(self, method, *args, **kwargs):
        cancel_request = False
        variables = self.variables(*args)
        try:
            self._validate_input("get", *args, **kwargs)
        except ValidationError as exc:
            if variables["url"].startswith("http"):
                raise exc
            # Wrong protocol given, like: x-raw-image://
            self.set_error(404)
            cancel_request = True
        return self.validate_request({
            "args": args,
            "kwargs": kwargs,
            "method": "get",
            "url": variables["url"],
            "headers": {},
            "data": None,
            "cancel": cancel_request
        }, validate_input=False)

    def _get_file_class(self):
        return File

    def _get_file_info(self, url):
        path = str(URLObject(url).path)
        tail, head = os.path.split(path)
        name, extension = os.path.splitext(head)
        now = datetime.utcnow()
        file_name = "{}.{}".format(
            now.strftime(settings.DATAGROWTH_DATETIME_FORMAT),
            name
        )
        return file_name, extension

    def _save_file(self, url, content):
        file_name, extension = self._get_file_info(url)
        if len(file_name) > 150:
            file_name = file_name[:150]
            file_name += extension
        if len(file_name) > 155:
            file_name = file_name[:155]
        FileClass = self._get_file_class()
        file = FileClass(BytesIO(content))
        file_name = default_storage.save('downloads/' + file_name, file)
        return file_name

    def _update_from_response(self, response):
        file_name = self._save_file(self.request["url"], response.content)
        self.head = dict(response.headers)
        self.status = response.status_code
        self.body = file_name

    @property
    def content(self):
        if self.success:
            content_type = self.head.get("content-type", "unknown/unknown").split(';')[0]
            file = default_storage.open(self.body)
            try:
                return content_type, file
            except IOError:
                return None, None
        return None, None

    def post(self, *args, **kwargs):
        raise NotImplementedError("You can't download an image over POST")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.timeout = kwargs.get("timeout", 4)

    class Meta:
        abstract = True
