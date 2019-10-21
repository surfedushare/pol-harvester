import logging
from tqdm import tqdm

from pol_harvester.models import Freeze, Collection, Arrangement
from pol_harvester.management.base import OutputCommand, FreezeCommand
from pol_harvester.utils.logging import log_header
from pol_harvester.readers.library4learning import WurLibrary4Learning


log = logging.getLogger(__name__)
out = logging.getLogger("freeze")


class Command(OutputCommand):


    def add_arguments(self, parser):
        parser.add_argument('-i', '--input', type=str, required=True,
                            help="The directory containing the XML dump files")
        parser.add_argument('-f', '--freeze', type=str, required=True)
        parser.add_argument('-c', '--collection', type=str, required=True)

    def _get_or_create_context(self, freeze_name, collection_name):
        freeze, created = Freeze.objects.get_or_create(name=freeze_name)
        freeze.referee = "id"
        freeze.save()
        if created:
            log.info("Created freeze " + freeze_name)
        else:
            log.info("Adding to freeze " + freeze_name)
        collection, created = Collection.objects.get_or_create(name=collection_name, freeze=freeze)
        collection.referee = "id"
        collection.save()
        if created:
            log.info("Created collection " + collection_name)
        else:
            log.info("Adding to collection " + collection_name)
        return freeze, collection

    def handle(self, *args, **options):

        log_header(out, "FREEZE LIBRARY 4 LEARNING", options)

        freeze, collection = self._get_or_create_context(options["freeze"], options["collection"])
        dumped = 0
        docs = 0

        wur = WurLibrary4Learning(options["input"])
        errors = wur.load()
        out.info("Amount of WUR Library load errors: {}".format(errors))
        wur_urls = list(wur)
        out.info("Amount of extracted WUR URLs: {}".format(len(wur_urls)))

        for record in tqdm(wur_urls):
            documents = []
            for document in record.get("documents", []):
                documents.append(self._create_document(document["text"], document, pipeline={"raw": True}))
            dumped += 1
            docs += len(documents)

            arrangement = Arrangement.objects.create(
                freeze=freeze,
                collection=collection,
                schema={},
                referee="id",
                meta={
                    "id": record["id"],
                    "url": record["url"],
                    "keywords": record["keywords"]
                }
            )
            if len(documents):
                arrangement.add(documents, collection=collection)

        out.info("Dumped Arrangements: {}".format(dumped))
        out.info("Dumped Documents: {}".format(docs))
