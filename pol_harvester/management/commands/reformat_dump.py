import logging
import os
import json
from tqdm import tqdm

from pol_harvester.management.base import DumpCommand


log = logging.getLogger(__name__)


class Command(DumpCommand):

    def handle(self, *args, **options):

        with open(options["input"], "r") as json_file:
            records = json.load(json_file)

        base_dir = options["output"]
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)

        with_text = []

        for record in tqdm(records):
            documents = []
            for document in record.get("documents", []):
                documents.append(self._create_document(document["text"], document))

            identifier = record["id"]
            output = {
                "id": identifier,
                "url": record["url"],
                "keywords": record["keywords"],
                "documents": documents
            }

            with open(os.path.join(base_dir, identifier + ".json"), "w") as record_file:
                json.dump(output, record_file)

            if any((doc for doc in documents if doc["text"] is not None)):
                with_text.append(output)

        with open(os.path.join(base_dir, "with_text.json"), "w") as record_file:
            json.dump(with_text, record_file, indent=4)
