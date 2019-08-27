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

        # TODO: get the EdurepFile+Tika objects for the videos and determine video strategy from there
        # TODO: how can EdurepFile+TIka help with the IMSCP content?
        video_urls = []
        skipped = 0
        for record in records:
            url = URLObject(record["url"])
            if not url.hostname in VIDEO_DOMAINS:
                if record["mime_type"] and record["mime_type"].startswith("video"):
                    skipped += 1
                continue
            video_urls.append(record["url"])

        successes, errors = run_serie(
            tqdm([
                [url] for url in video_urls
            ]),
            [
                {} for _ in video_urls
            ],
            config=config
        )

        out.info("Skipped video content due to domain restrictions: {}".format(skipped))
        out.info("Errors while downloading audio from videos: {}".format(len(errors)))
        out.info("Audio downloaded successfully: {}".format(len(successes)))
