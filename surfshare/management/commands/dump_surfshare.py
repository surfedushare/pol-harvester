import logging
import os
import json
from urlobject import URLObject

from django.core.management.base import BaseCommand

from datagrowth.exceptions import DGResourceException
from pol_harvester.models import YouTubeDLResource, KaldiNLResource


log = logging.getLogger(__name__)


VIDEO_DOMAINS = [
    'www.youtube.com',
    'lecturenet.uu.nl',
    'vimeo.com',
    'player.ou.nl',
]


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-i', '--input', type=str, required=True)
        parser.add_argument('-o', '--output', type=str, required=True)

    def get_video_text(self, document):
        try:
            download = YouTubeDLResource().run(document["url"])
        except DGResourceException:
            return
        _, file_path = download.content
        if file_path is None:
            log.warning("Could not find download for: {}".format(document["url"]))
            return
        transcription = KaldiNLResource().run(file_path)
        _, transcript = transcription.content
        if transcript is None:
            log.warning("Could not find transcription for: {}".format(document["url"]))
        return transcript

    def handle(self, *args, **options):

        base_dir = options["output"]
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)

        with_text = []

        for path, dirs, files in os.walk(options["input"]):
            for file in files:
                with open(os.path.join(path, file), "r") as json_file:
                    data = json.load(json_file)
                documents = []
                has_text = False
                for document in data.get("documents", []):
                    if URLObject(document["url"]).hostname in VIDEO_DOMAINS:
                        text = self.get_video_text(document)
                        document["text"] = text
                        document["mime_type"] = "video/mp4"  # TODO: detect correct type?
                        del document["exception"]
                    else:
                        document["mime_type"] = document["content-type"]
                        del document["content-type"]
                    has_text = has_text or document["text"] is not None
                    documents.append(document)
                data["documents"] = documents
                if has_text:
                    with_text.append(data)
                with open(os.path.join(base_dir, file), "w") as json_file:
                    json.dump(data, json_file)

        with open(os.path.join(base_dir, "with_text.json"), "w") as record_file:
            json.dump(with_text, record_file, indent=4)
