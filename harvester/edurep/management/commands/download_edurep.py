import logging
import json

from django.core.management.base import BaseCommand

from datagrowth.resources.http.tasks import send_serie
from pol_harvester.utils.logging import log_header


out = logging.getLogger("freeze")


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-i', '--input', type=str, required=True)

    def handle(self, *args, **options):

        log_header(out, "EDUREP DOWNLOAD WEB CONTENT", options)

        with open(options["input"], "r") as json_file:
            records = json.load(json_file)

        config = {
            "resource": "edurep.EdurepFile",
            "_namespace": "http_resource",
            "_private": ["_private", "_namespace", "_defaults"]
        }

        successes, errors = send_serie(
            [[record["url"]] for record in records],
            [{} for _ in records],
            config=config,
            method="get"
        )

        out.info("Errors while downloading content: {}".format(len(errors)))
        out.info("Content downloaded successfully: {}".format(len(successes)))
