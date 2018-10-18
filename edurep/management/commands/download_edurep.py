import json

from django.core.management.base import BaseCommand

from datagrowth.resources.http.tasks import send_serie


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-i', '--input', type=str, required=True)

    def handle(self, *args, **options):

        with open(options["input"], "r") as json_file:
            records = json.load(json_file)

        config = {
            "resource": "edurep.EdurepFile",
            "_namespace": "http_resource",
            "_private": ["_private", "_namespace", "_defaults"]
        }

        send_serie(
            [[record["source"]] for record in records],
            [{} for _ in records],
            config=config,
            method="get"
        )
