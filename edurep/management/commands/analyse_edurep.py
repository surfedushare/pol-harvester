import json
import pandas as pd
from urlobject import URLObject

from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-i', '--input', type=str, required=True)

    def handle(self, *args, **options):

        with open(options["input"], "r") as json_file:
            records = json.load(json_file)

        def normalize_source(entry):
            url = URLObject(entry["source"])
            entry["source"] = url.hostname
            return entry

        df = pd.DataFrame([normalize_source(record) for record in records])
        print(df.groupby("language").size().reset_index(name='counts'))
        print(df.groupby("mime_type").size().reset_index(name='counts'))
        print(df.groupby("source").size().reset_index(name='counts'))
