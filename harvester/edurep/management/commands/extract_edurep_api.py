import logging
import json

from django.core.management.base import BaseCommand

from datagrowth.processors import ExtractProcessor
from pol_harvester.utils.logging import log_header
from edurep.models import EdurepSearch


out = logging.getLogger("freeze")
err = logging.getLogger("pol_harvester")


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-o', '--output', type=str)
        parser.add_argument('-q', '--query', type=str, default="")

    def handle(self, *args, **options):

        log_header(out, "EDUREP API SEARCH EXTRACTION")

        # Determine which set of Edurep API responses to consider
        query = options["query"]
        if query:
            queryset = EdurepSearch.objects.filter(request__contains=query)
        else:
            queryset = EdurepSearch.objects.all()

        # First we determine how much failures
        failures = queryset.exclude(status=200).count()
        out.info("Amount of failed Edurep API queries: {}".format(failures))
        successes = queryset.filter(status=200).count()
        out.info("Amount of successful Edurep API queries: {}".format(successes))

        # Configure and create a data extractor
        config = {
            "objective": {
                "@": "soup.find_all('srw:record')",
                "url": "el.find('czp:location').text",
                "title": "el.find('czp:title').find('czp:langstring').text",
                "language": "el.find('czp:language').text",
                "keywords": "[keyword.find('czp:langstring').text for keyword in el.find_all('czp:keyword')]",
                "description": "el.find('czp:description').find('czp:langstring').text if el.find('czp:description') else None",
                "mime_type": "el.find('czp:format').text",
            }
        }
        prc = ExtractProcessor(config=config)
        rsl = []

        # Extract and count per query
        results_by_query = {}
        for search in queryset.filter(status=200):
            try:
                query = search.request["args"][0]
                if query not in results_by_query:
                    results_by_query[query] = 0
                qrsl = list(prc.extract_from_resource(search))
                results_by_query[query] += len(qrsl)
                rsl += qrsl
            except ValueError as exc:
                err.warning("Invalid XML:", exc, search.uri)

        out.info("Amount of extracted results by API query:")
        out.info(json.dumps(results_by_query, indent=4))

        # Write to disk when output file is given
        output_file = options.get("output", None)
        if not output_file:
            return
        with open(output_file, "w") as json_file:
            json.dump(rsl, json_file, indent=4)
