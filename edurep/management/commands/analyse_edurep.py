import json
import pandas as pd
from urlobject import URLObject

from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):

        with open("edurep/data/resources.json", "r") as json_file:
            records = json.load(json_file)

        def normalize_source(entry):
            url = URLObject(entry["source"])
            entry["source"] = url.hostname
            return entry

        df = pd.DataFrame([normalize_source(record) for record in records])
        print(df.groupby("language").size().reset_index(name='counts'))
        print(df.groupby("mime_type").size().reset_index(name='counts'))
        print(df.groupby("source").size().reset_index(name='counts'))
