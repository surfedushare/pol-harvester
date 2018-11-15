import os
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
            "resource": "pol_harvester.KaldiNLResource",
            "_namespace": "shell_resource",
            "_private": ["_private", "_namespace", "_defaults"]
        }

        for video_url in tqdm(video_urls):
            try:
                download = YouTubeDLResource().run(video_url)
            except DGShellError:
                continue
            _, file_path = download.content
            if file_path is None:
                log.warning("Could not find download for: {}".format(video_url))
                continue
            run(file_path, config=config)
