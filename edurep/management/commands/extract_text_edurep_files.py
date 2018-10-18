import json
import pandas as pd

import matplotlib.pyplot as plt

from django.core.management.base import BaseCommand

from datagrowth.resources.http.tasks import send_serie
from edurep.models import EdurepFile


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-i', '--input', type=str, required=True)
        parser.add_argument('-f', '--formats', type=str, default="")

    def handle(self, *args, **options):

        with open(options["input"], "r") as json_file:
            records = json.load(json_file)

        df = pd.DataFrame(records)
        formats = options["formats"]
        if not formats:
            mime_type_count = df.groupby("mime_type").size().reset_index(name='counts')
            mime_type_count.plot(kind="barh", x="mime_type", y="counts")
            plt.show()
            return

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
