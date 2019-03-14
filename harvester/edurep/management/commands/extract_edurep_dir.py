import logging
import os
import json
from bs4 import BeautifulSoup

from django.core.management.base import BaseCommand

from datagrowth.processors import ExtractProcessor
from pol_harvester.utils.logging import log_header


out = logging.getLogger("freeze")
err = logging.getLogger("pol_harvester")


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-i', '--input', type=str, required=True)
        parser.add_argument('-o', '--output', type=str)

    def handle(self, *args, **options):

        log_header(out, "EDUREP XML DUMP EXTRACTION", options)

        # Configure and create a data extractor
        config = {
            "objective": {
                "@": "soup.find('czp:lom')",
                "url": "el.find('czp:location').text",
                "title": "el.find('czp:title').find('czp:langstring').text",
                "language": "el.find('czp:language').text",
                "keywords": "[keyword.find('czp:langstring').text for keyword in el.find_all('czp:keyword')]",
                "description": "el.find('czp:description').find('czp:langstring').text",
                "mime_type": "el.find('czp:format').text",
            }
        }
        prc = ExtractProcessor(config=config)

        # Walk the directory and extract files
        rsl = []
        results_by_file = {}
        for root, dirs, files in os.walk(options["input"]):
            for file in files:
                if file.startswith(".") or file.endswith("txt"):
                    continue
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="latin-1") as file_obj:
                    content = file_obj.read()
                    soup = BeautifulSoup(content, "lxml")
                    try:
                        if file not in results_by_file:
                            results_by_file[file] = 0
                        frsl = list(prc.extract("text/xml", soup))
                        results_by_file[file] += len(frsl)
                        rsl += frsl
                    except ValueError as exc:
                        err.warning("Invalid XML:", exc, file_path)

        out.info("Amount of extracted results from XML dump:")
        out.info(json.dumps(results_by_file, indent=4))

        # Write to disk when output file is given
        output_file = options.get("output", None)
        if not output_file:
            return
        with open(output_file, "w") as json_file:
            json.dump(rsl, json_file, indent=4)
