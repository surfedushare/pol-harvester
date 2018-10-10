import os
import json
from uuid import uuid4

from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-i', '--input', type=str, required=True)
        parser.add_argument('-o', '--output', type=str, required=True)

    def handle(self, *args, **options):

        with open(options["input"], "r") as json_file:
            records = json.load(json_file)

        base_dir = options["output"]
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)

        for record in records:
            identifier = str(uuid4())
            output = {
                "id": identifier,
                "url": record["source"],
                "keywords": record["keywords"],
                "documents": [
                    {
                        "title": record["title"],
                        "url": record["source"],
                        "text": None,
                        "content-type": record["mime_type"]
                    }
                ]
            }
            with open(os.path.join(base_dir, identifier + ".json"), "w") as record_file:
                json.dump(output, record_file)
