import json

from django.core.management.base import BaseCommand

from datagrowth.processors import ExtractProcessor
from edurep.models import EdurepSearch


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-o', '--output', type=str, required=True)
        parser.add_argument('-q', '--query', type=str, default="")

    def handle(self, *args, **options):

        config = {
            "objective": {
                "@": "soup.find_all('srw:record')",
                "title": "el.find('czp:title').find('czp:langstring').text",
                "language": "el.find('czp:language').text",
                "keywords": "[keyword.find('czp:langstring').text for keyword in el.find_all('czp:keyword')]",
                "description": "el.find('czp:description').find('czp:langstring').text if el.find('czp:description') else None",
                "mime_type": "el.find('czp:format').text",
                "source": "el.find('czp:location').text",
            }
        }
        prc = ExtractProcessor(config=config)
        rsl = []
        query = options["query"]
        if query:
            queryset = EdurepSearch.objects.filter(request__contains=query)
        else:
            queryset = EdurepSearch.objects.all()
        for search in queryset:
            try:
                rsl += prc.extract_from_resource(search)
            except ValueError as exc:
                print("Invalid XML:", exc, search.uri)


        with open(options["output"], "w") as json_file:
            json.dump(rsl, json_file, indent=4)
