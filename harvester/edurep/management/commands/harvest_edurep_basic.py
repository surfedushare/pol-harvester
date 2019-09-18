import logging
from tqdm import tqdm
import pandas as pd
import json

from django.core.management.base import BaseCommand
from django.utils.timezone import now

from datagrowth.resources.http.tasks import send, send_serie
from datagrowth.configuration import create_config
from pol_harvester.constants import HarvestStages
from pol_harvester.utils.logging import log_header
from edurep.models import EdurepHarvest, EdurepFile
from edurep.utils import get_edurep_query_seeds


out = logging.getLogger("freeze")
err = logging.getLogger("pol_harvester")


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-f', '--freeze', type=str, required=True)
        parser.add_argument('-s', '--skip-mime-types', type=str, default="")

    def fetch_edurep_data(self, harvest_queryset):
        send_config = create_config("http_resource", {
            "resource": "edurep.EdurepSearch",
            "continuation_limit": 1000,
        })
        for harvest in tqdm(harvest_queryset, total=harvest_queryset.count()):
            query = harvest.source.query
            success, error = send(query, config=send_config, method="get")
            out.info('Amount of failed Edurep API queries for "{}": {}'.format(query, len(error)))
            out.info('Amount of successful Edurep API queries for "{}": {}'.format(query, len(success)))
            out.info('')

    def download_seed_files(self, seeds):
        download_config = create_config("http_resource", {
            "resource": "edurep.EdurepFile",
        })
        success, error = send_serie(
            tqdm([[seed["url"]] for seed in seeds]),
            [{} for _ in seeds],
            config=download_config,
            method="get"
        )
        out.info("Errors while downloading content: {}".format(len(error)))
        out.info("Content downloaded successfully: {}".format(len(success)))
        return success

    def extract_from_seed_files(self, seeds, downloads, mime_type_blacklist):
        df = pd.DataFrame(seeds)
        keeps = df.loc[~df['mime_type'].isin(mime_type_blacklist)]
        skips = df.loc[df['mime_type'].isin(mime_type_blacklist)]
        mime_type_counts = keeps.groupby("mime_type").size().to_dict()
        uris = [EdurepFile.uri_from_url(url) for url in list(keeps["url"])]
        file_resources = EdurepFile.objects.filter(uri__in=uris, id__in=downloads)

        out.info("Included mime types for download: {}".format(json.dumps(mime_type_counts, indent=4)))
        out.info("Skipped URL's due to mime_type: {}".format(skips.shape[0]))

        tika_config = create_config("http_resource", {
            "resource": "pol_harvester.HttpTikaResource",
        })
        success, error = send_serie(
            tqdm([[] for _ in file_resources]),
            [{"file": resource.body} for resource in file_resources],
            config=tika_config,
            method="post"
        )

        out.info("Errors while extracting texts: {}".format(len(error)))
        out.info("Texts extracted successfully: {}".format(len(success)))

    def handle(self, *args, **options):

        freeze_name = options["freeze"]
        mime_type_blacklist = options["skip_mime_types"].split(",") if options["skip_mime_types"] else []

        harvest_queryset = EdurepHarvest.objects.filter(
            freeze__name=freeze_name,
            stage=HarvestStages.NEW,
            scheduled_after__lt=now()
        )
        if not harvest_queryset.exists():
            raise EdurepHarvest.DoesNotExist(
                f"There are no scheduled and NEW EdurepHarvest objects for '{freeze_name}'"
            )

        log_header(out, "EDUREP BASIC HARVEST", options)

        # First step is to call the Edurep API and get the Edurep meta data about materials
        print("Fetching data for sources ...")
        self.fetch_edurep_data(harvest_queryset)

        # From the Edurep API metadata we generate "seeds" that are the starting point for our own data structure
        print("Extracting data from sources ...")
        seeds = []
        for harvest in tqdm(harvest_queryset, total=harvest_queryset.count()):
            query = harvest.source.query
            query_seeds = get_edurep_query_seeds(query)
            out.info('Amount of extracted results by API query for "{}": {}'.format(query, len(query_seeds)))
            seeds += query_seeds
        out.info("")

        # Download files of all seeds
        print("Downloading files ...")
        download_ids = self.download_seed_files(seeds)

        # Process files with Tika to extract data from content
        print("Extracting basic content from files ...")
        self.extract_from_seed_files(seeds, download_ids, mime_type_blacklist)

        # Finish the basic harvest
        for harvest in harvest_queryset:
            harvest.stage = HarvestStages.BASIC
            harvest.save()
