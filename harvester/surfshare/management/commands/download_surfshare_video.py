import logging
import os
from tqdm import tqdm
import json
from urlobject import URLObject

from django.core.management.base import BaseCommand

from datagrowth.resources.shell.tasks import run_serie
from surfshare.constants import VIDEO_DOMAINS


out = logging.getLogger("freeze")


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-i', '--input', type=str, required=True)

    def handle(self, *args, **options):

        video_urls = []
        skipped_mime_type = 0
        skipped_domain = 0
        for path, dirs, files in os.walk(options["input"]):
            for file in files:
                with open(os.path.join(path, file)) as json_file:
                    data = json.load(json_file)
                    for document in data.get("documents", []):
                        mime_type = document.get("content-type", None)  # NB: content-type is wrong legacy naming
                        if mime_type is None:
                            skipped_mime_type += 1
                        url = URLObject(document["url"])
                        if url.hostname not in VIDEO_DOMAINS:
                            if mime_type.startswith("video"):
                                skipped_domain += 1
                            continue
                        if "youtube.com" in url.hostname:
                            url = url.del_query_param('list')
                            url = url.del_query_param('index')
                        video_urls.append(str(url))

        config = {
            "resource": "pol_harvester.YouTubeDLResource",
            "_namespace": "http_resource",
            "_private": ["_private", "_namespace", "_defaults"]
        }

        successes, errors = run_serie(
            tqdm([
                [url] for url in video_urls
            ]),
            [
                {} for record in video_urls
            ],
            config=config
        )

        out.info("Skipped video content due to missing mime type: {}".format(skipped_mime_type))
        out.info("Skipped video content due to domain restrictions: {}".format(skipped_domain))
        out.info("Errors while downloading audio from videos: {}".format(len(errors)))
        out.info("Audio downloaded successfully: {}".format(len(successes)))
