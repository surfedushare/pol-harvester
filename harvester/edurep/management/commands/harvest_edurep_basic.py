import pandas as pd
import json

from datagrowth.resources.http.tasks import send_serie
from datagrowth.configuration import create_config
from pol_harvester.management.base import HarvesterCommand
from pol_harvester.constants import HarvestStages
from edurep.models import EdurepHarvest, EdurepFile
from edurep.utils import get_edurep_oaipmh_seeds


class Command(HarvesterCommand):

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('-f', '--freeze', type=str, required=True)
        parser.add_argument('-s', '--skip-mime-types', type=str, default="")

    def download_seed_files(self, seeds):
        download_config = create_config("http_resource", {
            "resource": "edurep.EdurepFile",
        })
        success, error = send_serie(
            self.progress([[seed["url"]] for seed in seeds]),
            [{} for _ in seeds],
            config=download_config,
            method="get"
        )
        self.info("Errors while downloading content: {}".format(len(error)))
        self.info("Content downloaded successfully: {}".format(len(success)))
        return success

    def extract_from_seed_files(self, seeds, downloads, mime_type_blacklist):
        df = pd.DataFrame(seeds)
        keeps = df.loc[~df['mime_type'].isin(mime_type_blacklist)]
        skips = df.loc[df['mime_type'].isin(mime_type_blacklist)]
        mime_type_counts = keeps.groupby("mime_type").size().to_dict()
        uris = [EdurepFile.uri_from_url(url) for url in list(keeps["url"])]
        file_resources = EdurepFile.objects.filter(uri__in=uris, id__in=downloads)

        self.info("Included mime types for download: {}".format(json.dumps(mime_type_counts, indent=4)))
        self.info("Skipped URL's due to mime_type: {}".format(skips.shape[0]))

        tika_config = create_config("http_resource", {
            "resource": "pol_harvester.HttpTikaResource",
        })
        success, error = send_serie(
            self.progress([[] for _ in file_resources]),
            [{"file": resource.body} for resource in file_resources],
            config=tika_config,
            method="post"
        )

        self.info("Errors while extracting texts: {}".format(len(error)))
        self.info("Texts extracted successfully: {}".format(len(success)))

    def handle(self, *args, **options):

        freeze_name = options["freeze"]
        mime_type_blacklist = options["skip_mime_types"].split(",") if options["skip_mime_types"] else []

        harvest_queryset = EdurepHarvest.objects.filter(
            freeze__name=freeze_name,
            stage=HarvestStages.NEW
        )
        if not harvest_queryset.exists():
            raise EdurepHarvest.DoesNotExist(
                f"There are no scheduled and NEW EdurepHarvest objects for '{freeze_name}'"
            )

        self.header("EDUREP BASIC HARVEST", options)

        # From the Edurep API metadata we generate "seeds" that are the starting point for our own data structure
        self.info("Extracting data from sources ...")
        seeds = []
        progress = {}
        for harvest in self.progress(harvest_queryset, total=harvest_queryset.count()):
            set_specification = harvest.source.collection_name
            harvest_seeds = get_edurep_oaipmh_seeds(
                set_specification,
                harvest.latest_update_at,
                include_deleted=False
            )
            seeds += harvest_seeds
            progress[set_specification] = len(harvest_seeds)
        for set_name, seeds_count in progress.items():
            self.info(f'Amount of extracted results by OAI-PMH for "{set_name}": {seeds_count}')
        self.info("")

        # Download files of all seeds
        self.info("Downloading files ...")
        download_ids = self.download_seed_files(seeds)

        # Process files with Tika to extract data from content
        self.info("Extracting basic content from files ...")
        self.extract_from_seed_files(seeds, download_ids, mime_type_blacklist)

        # Finish the basic harvest
        for harvest in harvest_queryset:
            harvest.stage = HarvestStages.BASIC
            harvest.save()
