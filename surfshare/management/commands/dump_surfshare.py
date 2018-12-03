import os
import json
from urlobject import URLObject

from pol_harvester.management.base import DumpCommand
from surfshare.constants import VIDEO_DOMAINS


class Command(DumpCommand):

    def handle(self, *args, **options):

        base_dir = options["output"]
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)

        with_text = []

        for path, dirs, files in os.walk(options["input"]):
            for file in files:
                with open(os.path.join(path, file), "r") as json_file:
                    data = json.load(json_file)
                documents = []
                for document in data.get("documents", []):
                    content_type = document.get("content-type", None)
                    document["mime_type"] = content_type
                    if content_type:
                        del document["content-type"]
                    if URLObject(document["url"]).hostname in VIDEO_DOMAINS:
                        documents += self.get_documents_from_kaldi(document)
                    else:
                        documents.append(self._create_document(document["text"], document))
                data["documents"] = documents

                if any((doc for doc in documents if doc["text"] is not None)):
                    with_text.append(data)

                with open(os.path.join(base_dir, file), "w") as json_file:
                    json.dump(data, json_file)

        with open(os.path.join(base_dir, "with_text.json"), "w") as record_file:
            json.dump(with_text, record_file, indent=4)
