import os
import json
from bs4 import BeautifulSoup

from django.core.management.base import BaseCommand

from datagrowth.processors import ExtractProcessor


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-i', '--input', type=str, required=True)
        parser.add_argument('-o', '--output', type=str, required=True)

    def handle(self, *args, **options):

        config = {
            "objective": {
                "@": "$",
                "title": "$.title",
                "language": "$.language.0",
                "keywords": "$.keyword",
                "description": "$.description",
                "mime_type": "$.format.mimetype",
                "source": "$.url.location",
            }
        }
        prc = ExtractProcessor(config=config)

        with open(options["input"], "r", encoding="utf-8") as json_file:
            content = json.load(json_file)
        rsl = list(prc.extract("application/json", content))

        with open(options["output"], "w") as json_file:
            json.dump(rsl, json_file, indent=4)
