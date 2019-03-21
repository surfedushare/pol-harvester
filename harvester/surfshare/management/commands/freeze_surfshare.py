import os
import json
from urlobject import URLObject
from tqdm import tqdm

from pol_harvester.management.base import DumpCommand, FreezeCommand
from pol_harvester.models import Arrangement
from surfshare.constants import VIDEO_DOMAINS


class Command(FreezeCommand, DumpCommand):

    def handle(self, *args, **options):

        freeze, collection = self._get_or_create_context(options["freeze"], options["collection"])

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

                arrangement = Arrangement.objects.create(
                    freeze=freeze,
                    collection=collection,
                    schema={},
                    referee="id",
                    meta={
                        "id": data["id"],
                        "url": data["url"],
                        "keywords": data["keywords"]
                    }
                )
                if len(documents):
                    arrangement.add(documents, collection=collection)
