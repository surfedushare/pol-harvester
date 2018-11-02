import logging
from tqdm import tqdm
import json
from urlobject import URLObject

from django.core.management.base import BaseCommand

from datagrowth.resources.shell.tasks import run
from datagrowth.exceptions import DGShellError
from pol_harvester.models import YouTubeDLResource


log = logging.getLogger(__name__)


VIDEO_DOMAINS = [
    # "mediasite.hro.nl",  # TODO: https://github.com/SURFpol/pol-harvester/issues/2
    # "video.saxion.nl",  # TODO: https://github.com/SURFpol/pol-harvester/issues/3
    # NB: Ted is the only English one at the moment, we exclude it for now
]


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-i', '--input', type=str, required=True)

    def handle(self, *args, **options):

        with open(options["input"], "r") as json_file:
            records = json.load(json_file)

        config = {
            "resource": "pol_harvester.KaldiNLResource",
            "_namespace": "shell_resource",
            "_private": ["_private", "_namespace", "_defaults"]
        }
        video_records = [
            record for record in records
            if record["mime_type"].startswith("video") or
            URLObject(record["source"]).hostname in VIDEO_DOMAINS
        ]
        for video_record in tqdm(video_records):
            try:
                download = YouTubeDLResource().run(video_record["source"])
            except DGShellError:
                continue
            _, file_path = download.content
            if file_path is None:
                log.warning("Could not find download for: {}".format(video_record["source"]))
                continue
            run(file_path, config=config)
