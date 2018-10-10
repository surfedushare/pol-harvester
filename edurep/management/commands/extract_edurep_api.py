import json

from django.core.management.base import BaseCommand

from datagrowth.processors import ExtractProcessor
from edurep.models import EdurepSearch


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-o', '--output', type=str, required=True)

    def handle(self, *args, **options):

        config = {
            "objective": {
                "@": "soup.find_all('srw:record')",
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
        for search in EdurepSearch.objects.all():
            rsl += prc.extract_from_resource(search)

        with open(options["output"], "w") as json_file:
            json.dump(rsl, json_file, indent=4)
