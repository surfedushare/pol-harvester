import logging
import json

from django.core.management.base import BaseCommand

from datagrowth.processors import ExtractProcessor
from pol_harvester.utils.logging import log_header


out = logging.getLogger("freeze")


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-i', '--input', type=str, required=True)
        parser.add_argument('-o', '--output', type=str)

    def handle(self, *args, **options):

        log_header(out, "EDUREP JSON EXTRACTION", options)

        config = {
            "objective": {
                "@": "$",
                "url": "$.url.location",
                "title": "$.title",
                "language": "$.language.0",
                "keywords": "$.keyword",
                "description": "$.description",
                "mime_type": "$.format.mimetype",
            }
        }
        prc = ExtractProcessor(config=config)

        with open(options["input"], "r", encoding="utf-8") as json_file:
            content = json.load(json_file)
        rsl = list(prc.extract("application/json", content))

        out.info("Amount of extracted results from JSON: {}".format(len(rsl)))

        # Write to disk when output file is given
        output_file = options.get("output", None)
        if not output_file:
            return
        with open(output_file, "w") as json_file:
            json.dump(rsl, json_file, indent=4)
