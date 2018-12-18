import os
import json
from urlobject import URLObject

from django.core.management.base import BaseCommand

from edurep.constants import VIDEO_DOMAINS as EDUREP_VIDEO_DOMAINS
from surfshare.constants import VIDEO_DOMAINS as SURFSHARE_VIDEO_DOMAINS


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-i', '--input', type=str, required=True)
        parser.add_argument('-o', '--output', type=str, required=True)

    def handle(self, *args, **options):

        rsl = []
        transcribed = 0
        for root, dirs, files in os.walk(options["input"]):
            for file in files:
                if file.startswith(".") or file.endswith("txt") or file == "with_text.json":
                    continue
                file_path = os.path.join(root, file)
                with open(file_path, "r") as file_obj:
                    data = json.load(file_obj)
                    for doc in data.get("documents", []):
                        url = URLObject(doc.get("url", None))
                        domain = url.hostname
                        language = doc.get("language", None)
                        text = doc.get("text", None)

                        if language == "en" and (domain in EDUREP_VIDEO_DOMAINS or domain in SURFSHARE_VIDEO_DOMAINS):
                            if not text:
                                rsl.append(doc)
                            else:
                                transcribed += 1

        print("Found {} English video documents without transcription and {} with a text".format(len(rsl), transcribed))
        with open(options["output"], "w") as json_file:
            json.dump(rsl, json_file, indent=4)
