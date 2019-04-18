import logging

from django.core.management.base import BaseCommand

from datagrowth.resources.http.tasks import send
from pol_harvester.utils.logging import log_header


out = logging.getLogger("freeze")


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-q', '--query', type=str, required=True)

    def handle(self, *args, **options):

        log_header(out, "HARVEST EDUREP API", options)

        config = {
            "resource": "edurep.EdurepSearch",
            "continuation_limit": 1000,
            "_namespace": "http_resource",
            "_private": ["_private", "_namespace", "_defaults"]
        }
        send(options["query"], config=config, method="get")
