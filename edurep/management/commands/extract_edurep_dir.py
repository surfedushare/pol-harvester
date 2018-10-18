import os
import json
from bs4 import BeautifulSoup

from django.core.management.base import BaseCommand

from datagrowth.processors import ExtractProcessor


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-o', '--output', type=str, required=True)

    def handle(self, *args, **options):

        config = {
            "objective": {
                "@": "soup.find('czp:lom')",
                "title": "el.find('czp:title').find('czp:langstring').text",
                "language": "el.find('czp:language').text",
                "keywords": "[keyword.find('czp:langstring').text for keyword in el.find_all('czp:keyword')]",
                "description": "el.find('czp:description').find('czp:langstring').text",
                "mime_type": "el.find('czp:format').text",
                "source": "el.find('czp:location').text",
            }
        }
        prc = ExtractProcessor(config=config)

        rsl = []
        for root, dirs, files in os.walk("data/ho-collections"):
            for file in files:
                if file.startswith(".") or file.endswith("txt"):
                    continue
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="latin-1") as file_obj:
                    content = file_obj.read()
                    soup = BeautifulSoup(content, "lxml")
                    try:
                        rsl += list(prc.extract("text/xml", soup))
                    except ValueError as exc:
                        print("Invalid XML:", exc, file_path)

        with open(options["output"], "w") as json_file:
            json.dump(rsl, json_file, indent=4)
