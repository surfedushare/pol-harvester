import json
import pandas as pd

from django.core.management.base import BaseCommand

from datagrowth.resources.http.tasks import send_serie
from edurep.models import EdurepFile
from edurep.constants import TIKA_MIME_TYPES


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-i', '--input', type=str, required=True)
        parser.add_argument('-f', '--formats', type=str, default=",".join(TIKA_MIME_TYPES))

    def handle(self, *args, **options):

        with open(options["input"], "r") as json_file:
            records = json.load(json_file)

        df = pd.DataFrame(records)
        formats = options["formats"]

        formats = formats.split(",")
        df = df.loc[df['mime_type'].isin(formats)]
        uris = [EdurepFile.uri_from_url(url) for url in list(df["source"])]
        file_resources = list(EdurepFile.objects.filter(uri__in=uris))

        config = {
            "resource": "pol_harvester.HttpTikaResource",
            "_namespace": "http_resource",
            "_private": ["_private", "_namespace", "_defaults"]
        }

        send_serie(
            [[] for _ in file_resources],
            [{"file": resource.body} for resource in file_resources],
            config=config,
            method="post"
        )
