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
        parser.add_argument('-o', '--output', type=str, required=True)

    def handle(self, *args, **options):

        freeze_name = options["freeze"]
        output_file = options["output"]

        harvest_queryset = EdurepHarvest.objects.filter(
            freeze__name=freeze_name,
            stage=HarvestStages.COMPLETE,
            scheduled_after__lt=now()
        )
        if not harvest_queryset.exists():
            raise EdurepHarvest.DoesNotExist(
                f"There are no scheduled and COMPLETE EdurepHarvest objects for '{freeze_name}'"
            )

        # From the Edurep API metadata we generate "seeds" that are the starting point for our own data structure
        print("Extracting data from sources ...")
        seeds = []
        for harvest in tqdm(harvest_queryset, total=harvest_queryset.count()):
            query = harvest.source.query
            query_seeds = get_edurep_query_seeds(query)
            for seed in query_seeds:
                seed["collection"] = harvest.source.collection_name
            print('Amount of extracted results by API query for "{}": {}'.format(query, len(query_seeds)))
            seeds += query_seeds

        # Dump seeds to specified file
        with open(output_file, "w") as output_file:
            json.dump(seeds, output_file, indent=4)

