import logging
from tqdm import tqdm
from collections import defaultdict
from zipfile import BadZipFile

from django.utils.timezone import now
from django.core.exceptions import ValidationError

from pol_harvester.models import Freeze, Collection, Arrangement
from pol_harvester.constants import HarvestStages
from pol_harvester.management.base import OutputCommand
from pol_harvester.utils.logging import log_header
from edurep.models import EdurepHarvest
from edurep.utils import get_edurep_query_seeds, get_edurep_resources
from ims.models import CommonCartridge


out = logging.getLogger("freeze")


class Command(OutputCommand):

    def add_arguments(self, parser):
        parser.add_argument('-f', '--freeze', type=str, required=True)

    def get_documents_from_transcription(self, transcription_resource, metadata, pipeline):
        if transcription_resource is None or not transcription_resource.success:
            transcript = None
        else:
            _, transcript = transcription_resource.content
        return [self._create_document(
            transcript,
            meta=metadata,
            pipeline=pipeline,
            file_type="video"
        )]

    def get_documents_from_zip(self, file_resource, tika_resource, metadata, pipeline):
        # Load zip as an IMS Common Cardridge
        cc = CommonCartridge(file=file_resource.body)
        try:
            cc.clean()
        except (ValidationError, BadZipFile):
            out.warning("Invalid or missing common cartridge for: {}".format(cc.id))
            return []
        # Extract texts per file in the Common Cartridge
        files = set()
        texts_by_file = defaultdict(list)
        for resource in cc.get_resources().values():
            files.update(resource["files"])
        tika_content_type, data = tika_resource.content
        if data is None:
            return False
        text = data.get("text", "")
        current_file = None
        for line in text.split("\n"):
            line = line.strip()
            if line in files:
                current_file = line
                continue
            if current_file and line:
                texts_by_file[current_file].append(line)
        # We temporarily disable creating multiple documents for a package
        # When there is a design to display courses in the portal we can re-enable this
        # Until that time concatenating all documents in a package to a single learning material
        # documents = {}
        # for file, texts in texts_by_file.items():
        #     doc = self._create_document(
        #         "\n".join(texts),
        #         url="{}/{}".format(metadata.get("package_url"), file),
        #         meta=metadata,
        #         pipeline=pipeline,
        #         hash_postfix=""  # updating URL to create unique hash instead, keeps legacy ids intact
        #     )
        #     documents[doc["id"]] = doc
        # return list(documents.values())
        text = ""
        for file, texts in texts_by_file.items():
            text += "\n".join(texts)
        return [self._create_document(
            text,
            url=metadata.get("package_url"),
            meta=metadata,
            pipeline=pipeline,
            hash_postfix=""  # updating URL to create unique hash instead, keeps legacy ids intact
        )]

    def get_documents(self, file_resource, tika_resource, metadata, pipeline):
        if tika_resource is None or not tika_resource.success:
            return []
        if tika_resource.is_zip():
            return self.get_documents_from_zip(file_resource, tika_resource, metadata, pipeline)
        if tika_resource.has_plain():
            tika_content_type, data = tika_resource.content
            if data is None:
                return []
            text = data.get("text", "")
            if not text:
                return []
            return [self._create_document(text, meta=metadata, pipeline=pipeline)]
        out.warning(f"No output at all for HttpTikaResource: {tika_resource.id}")
        return []

    def handle(self, *args, **options):

        freeze_name = options["freeze"]
        freeze, created = Freeze.objects.get_or_create(name=freeze_name)
        freeze.referee = "id"
        freeze.save()
        if created:
            out.info("Created freeze " + freeze_name)
        else:
            out.info("Adding to freeze " + freeze_name)

        harvest_queryset = EdurepHarvest.objects.filter(
            freeze__name=freeze_name,
            stage=HarvestStages.VIDEO,
            scheduled_after__lt=now()
        )
        if not harvest_queryset.exists():
            raise EdurepHarvest.DoesNotExist(
                f"There are no scheduled and VIDEO EdurepHarvest objects for '{freeze_name}'"
            )

        log_header(out, "FREEZE EDUREP", options)

        print("Extracting data from sources ...")
        seeds_by_collection = defaultdict(list)
        total_seeds = 0
        for harvest in tqdm(harvest_queryset, total=harvest_queryset.count()):
            query = harvest.source.query
            query_seeds = get_edurep_query_seeds(query)
            total_seeds += len(query_seeds)
            seeds_by_collection[harvest.source.collection_name] += query_seeds
        out.info(f"Files considered for processing: {total_seeds}")

        for collection_name, seeds in seeds_by_collection.items():

            # Get or create the collection this seed belongs to
            collection, created = Collection.objects.get_or_create(name=collection_name, freeze=freeze)
            collection.referee = "id"
            collection.save()
            if created:
                out.info("Created collection " + collection_name)
            else:
                out.info("Adding to collection " + collection_name)

            skipped = 0
            dumped = 0
            documents_count = 0
            print(f"Dumping {collection.name} ...")
            for seed in tqdm(seeds):
                url = seed["url"]
                if seed["mime_type"] == "application/x-Wikiwijs-Arrangement":
                    url += "?p=imscp"
                file_resource, tika_resource, video_resource, kaldi_resource = \
                    get_edurep_resources(seed["url"], seed.get("title", None))
                pipeline = {
                    "file": self._serialize_resource(file_resource),
                    "tika": self._serialize_resource(tika_resource),
                    "video": self._serialize_resource(video_resource),
                    "kaldi": self._serialize_resource(kaldi_resource)
                }
                has_video = tika_resource.has_video() if tika_resource is not None else False

                documents = []
                documents += self.get_documents(file_resource, tika_resource, seed, pipeline)
                if has_video:
                    documents += self.get_documents_from_transcription(kaldi_resource, seed, pipeline)

                if not len(documents):
                    skipped += 1
                    continue
                dumped += 1

                arrangement = Arrangement.objects.create(
                    freeze=freeze,
                    collection=collection,
                    schema={},
                    referee="id",
                    meta={
                        "reference_id": self.get_hash_from_url(seed["url"]),
                        "url": seed["url"],
                        "keywords": seed.get("keywords", [])
                    }
                )
                if len(documents):
                    arrangement.add(documents, collection=collection)
                    documents_count += len(documents)

            out.info(f"Skipped URL's for {collection.name} during dump: {skipped}")
            out.info(f"Dumped Arrangements for {collection.name}: {dumped}")
            out.info(f"Dumped Documents for {collection.name}: {documents_count}")

        # Finish the freeze and harvest
        for harvest in harvest_queryset:
            harvest.stage = HarvestStages.COMPLETE
            harvest.save()
