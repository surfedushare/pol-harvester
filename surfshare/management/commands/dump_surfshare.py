import os
import json
from urlobject import URLObject
from tqdm import tqdm

from pol_harvester.management.base import DumpCommand
from surfshare.constants import VIDEO_DOMAINS


class Command(DumpCommand):

    def handle(self, *args, **options):

        base_dir = options["output"]
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)

        with_text = []

        for path, dirs, files in os.walk(options["input"]):
            for file in tqdm(files):
                with open(os.path.join(path, file), "r") as json_file:
                    data = json.load(json_file)
                if "original_article" in data:
                    del data["original_article"]
                documents = []
                for document in data.get("documents", []):
                    content_type = document.get("content-type", None)
                    document["mime_type"] = content_type
                    if content_type:
                        del document["content-type"]
                    if not document.get("title", None):
                        document["title"] = data.get("title", None)
                    url = URLObject(document["url"])
                    if url.hostname in VIDEO_DOMAINS:
                        if "youtube.com" in url.hostname:
                            url = url.del_query_param('list')
                            url = url.del_query_param('index')
                            document["url"] = str(url)
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
