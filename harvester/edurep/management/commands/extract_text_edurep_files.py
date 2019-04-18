import logging
import json
import pandas as pd
from tqdm import tqdm

from django.core.management.base import BaseCommand

from datagrowth.resources.http.tasks import send_serie
from pol_harvester.utils.logging import log_header
from edurep.models import EdurepFile
from edurep.constants import TIKA_MIME_TYPES


out = logging.getLogger("freeze")


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-i', '--input', type=str, required=True)
        parser.add_argument('-f', '--formats', type=str, default=",".join(TIKA_MIME_TYPES))

    def handle(self, *args, **options):

        log_header(out, "EXTRACT EDUREP TEXT FILES", options)

        with open(options["input"], "r") as json_file:
            records = json.load(json_file)

        df = pd.DataFrame(records)
        formats = options["formats"]

        formats = formats.split(",")
        keeps = df.loc[df['mime_type'].isin(formats)]
        skips = df.loc[~df['mime_type'].isin(formats)]
        uris = [EdurepFile.uri_from_url(url) for url in list(keeps["url"])]
        relevant_mime_resources = EdurepFile.objects.filter(uri__in=uris)
        download_fail_count = relevant_mime_resources.exclude(status=200).count()
        file_resources = list(EdurepFile.objects.filter(status=200))

        config = {
            "resource": "pol_harvester.HttpTikaResource",
            "_namespace": "http_resource",
            "_private": ["_private", "_namespace", "_defaults"]
        }

        successes, errors = send_serie(
            tqdm([[] for _ in file_resources]),
            [{"file": resource.body} for resource in file_resources],
            config=config,
            method="post"
        )

        out.info("Skipped URL's due to mime_type: {}".format(skips.shape[0]))
        out.info("Skipped URL's due to download failure: {}".format(download_fail_count))
        out.info("Errors while extracting texts: {}".format(len(errors)))
        out.info("Texts extracted successfully: {}".format(len(successes)))
