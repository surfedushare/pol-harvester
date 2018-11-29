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

        video_urls = set()
        for path, dirs, files in os.walk(options["input"]):
            for file in files:
                with open(os.path.join(path, file)) as json_file:
                    data = json.load(json_file)
                    for document in data.get("documents", []):
                        url = URLObject(document["url"])
                        if url.hostname not in VIDEO_DOMAINS:
                            continue
                        if "youtube.com" in url.hostname:
                            url = url.del_query_param('list')
                            url = url.del_query_param('index')
                        video_urls.add(str(url))

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
            _, file_paths = download.content
            if not file_paths:
                log.warning("Could not find download(s) for: {}".format(video_url))
                continue
            for file_path in file_paths:
                run(file_path, config=config)
