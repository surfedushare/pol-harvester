import os
import json
import pandas as pd
from urlobject import URLObject

import matplotlib.pyplot as plt

from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-i', '--input', type=str, required=True)

    def handle(self, *args, **options):

        with open(options["input"], "r") as json_file:
            records = json.load(json_file)

        def normalize_source(entry):
            url = URLObject(entry["source"])
            entry["domain"] = url.hostname
            entry["path"], file_name = os.path.split(url.path)
            return entry

        df = pd.DataFrame([normalize_source(record) for record in records])

        # Plots
        language_count = df.groupby("language").size().reset_index(name='counts')
        mime_type_count = df.groupby("mime_type").size().reset_index(name='counts')
        domain_count = df.groupby("domain").size().reset_index(name='counts')
        language_count.plot(kind="barh", x="language", y="counts")
        mime_type_count.plot(kind="barh", x="mime_type", y="counts")
        domain_count.plot(kind="barh", x="domain", y="counts")
        plt.show()
