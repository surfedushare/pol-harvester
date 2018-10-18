import os
import json
import pandas as pd
from urlobject import URLObject
import requests
from tqdm import tqdm
import logging

from django.core.management.base import BaseCommand


log = logging.getLogger("pol_harvester")


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-i', '--input', type=str, required=True)

    def handle(self, *args, **options):

        with open(options["input"], "r") as json_file:
            records = json.load(json_file)[:100]

        def normalize_source(entry):
            url = URLObject(entry["source"])
            entry["domain"] = url.hostname
            entry["path"], file_name = os.path.split(url.path)
            return entry

        df = pd.DataFrame([normalize_source(record) for record in records])
        html = df[df["mime_type"]=="text/html"]
        html["status"] = pd.Series(index=html.index)
        for ix, row in tqdm(html.iterrows(), total=html.shape[0]):
            try:
                response = requests.get(row["source"])
            except Exception:
                log.error("Failure to GET: {}".format(row["source"]))
                html.loc[ix, "domain"] = "?"
                html.loc[ix, "status"] = 502
                continue
            url = URLObject(response.request.url)
            html.loc[ix, "domain"] = url.hostname
            html.loc[ix, "status"] = response.status_code

        print(html.groupby("domain").size().reset_index(name='counts'))
        print(html.groupby("status").size().reset_index(name='counts'))
