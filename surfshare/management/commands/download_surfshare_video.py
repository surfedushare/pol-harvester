import os
from tqdm import tqdm
import json
from urlobject import URLObject

from django.core.management.base import BaseCommand

from datagrowth.resources.shell.tasks import run_serie


VIDEO_DOMAINS = [
    'www.youtube.com',
    'lecturenet.uu.nl',
    'vimeo.com',
    'player.ou.nl',
]


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-i', '--input', type=str, required=True)

    def handle(self, *args, **options):

        video_urls = []
        for path, dirs, files in os.walk(options["input"]):
            for file in files:
                with open(os.path.join(path, file)) as json_file:
                    data = json.load(json_file)
                    for document in data.get("documents", []):
                        if URLObject(document["url"]).hostname in VIDEO_DOMAINS:
                            video_urls.append(document["url"])

        config = {
            "resource": "pol_harvester.YouTubeDLResource",
            "_namespace": "http_resource",
            "_private": ["_private", "_namespace", "_defaults"]
        }

        run_serie(
            tqdm([
                [url] for url in video_urls
            ]),
            [
                {} for record in video_urls
            ],
            config=config
        )
