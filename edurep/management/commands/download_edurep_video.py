from tqdm import tqdm
import json
from urlobject import URLObject

from django.core.management.base import BaseCommand

from datagrowth.resources.shell.tasks import run_serie


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
            "resource": "pol_harvester.YouTubeDLResource",
            "_namespace": "http_resource",
            "_private": ["_private", "_namespace", "_defaults"]
        }

        run_serie(
            tqdm([
                [record["source"]] for record in records
                if record["mime_type"].startswith("video") or
                URLObject(record["source"]).hostname in VIDEO_DOMAINS
            ]),
            [
                {} for record in records
                if record["mime_type"].startswith("video") or
                URLObject(record["source"]).hostname in VIDEO_DOMAINS
            ],
            config=config
        )
