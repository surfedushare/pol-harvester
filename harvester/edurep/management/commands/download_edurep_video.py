import logging
from tqdm import tqdm
import json
from urlobject import URLObject

from django.core.management.base import BaseCommand

from datagrowth.resources.shell.tasks import run_serie
from pol_harvester.utils.logging import log_header
from edurep.constants import VIDEO_DOMAINS


out = logging.getLogger("freeze")


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-i', '--input', type=str, required=True)

    def handle(self, *args, **options):

        log_header(out, "EDUREP DOWNLOAD AUDIO FROM VIDEOS", options)

        with open(options["input"], "r") as json_file:
            records = json.load(json_file)

        config = {
            "resource": "pol_harvester.YouTubeDLResource",
            "_namespace": "http_resource",
            "_private": ["_private", "_namespace", "_defaults"]
        }

        # TODO: handle video lists differently
        video_urls = []
        for record in records:
            url = URLObject(record["url"])
            if not url.hostname in VIDEO_DOMAINS:
                continue
            if "youtube.com" in url.hostname:
                url = url.del_query_param('list')
                url = url.del_query_param('index')
                record["url"] = str(url)
            video_urls.append(record["url"])

        errors, successes = run_serie(
            tqdm([
                [url] for url in video_urls
            ]),
            [
                {} for _ in video_urls
            ],
            config=config
        )

        out.info("Errors while downloading audio from videos: {}".format(len(errors)))
        out.info("Audio downloaded successfully: {}".format(len(successes)))
