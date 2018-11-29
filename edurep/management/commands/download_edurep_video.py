from tqdm import tqdm
import json
from urlobject import URLObject

from django.core.management.base import BaseCommand

from datagrowth.resources.shell.tasks import run_serie
from edurep.constants import VIDEO_DOMAINS


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
                if URLObject(record["source"]).hostname in VIDEO_DOMAINS
            ]),
            [
                {} for record in records
                if URLObject(record["source"]).hostname in VIDEO_DOMAINS
            ],
            config=config
        )
