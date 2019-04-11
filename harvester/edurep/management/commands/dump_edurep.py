import logging
import os
import json
from uuid import uuid4
from tqdm import tqdm
from urlobject import URLObject

from pol_harvester.management.base import OutputCommand
from edurep.constants import TIKA_MIME_TYPES, VIDEO_DOMAINS


log = logging.getLogger(__name__)


class Command(OutputCommand):

    def handle(self, *args, **options):

        with open(options["input"], "r") as json_file:
            records = json.load(json_file)

        base_dir = options["output"]
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)

        with_text = []

        for record in tqdm(records):
            identifier = str(uuid4())
            url = URLObject(record["source"])
            if url.hostname in VIDEO_DOMAINS:
                if "youtube.com" in url.hostname:
                    url = url.del_query_param('list')
                    url = url.del_query_param('index')
                record["source"] = str(url)
                documents = self.get_documents_from_kaldi(record)
            elif record["mime_type"] == "application/x-Wikiwijs-Arrangement":
                documents = self.get_documents_from_imscp(record)
            elif record["mime_type"] in TIKA_MIME_TYPES:
                documents = self.get_documents_from_tika(record)
            else:
                continue

            output = {
                "id": identifier,
                "url": record["source"],
                "keywords": record["keywords"],
                "documents": documents
            }
            with open(os.path.join(base_dir, identifier + ".json"), "w") as record_file:
                json.dump(output, record_file)

            if any((doc for doc in documents if doc["text"] is not None)):
                with_text.append(output)

        with open(os.path.join(base_dir, "with_text.json"), "w") as record_file:
            json.dump(with_text, record_file, indent=4)
