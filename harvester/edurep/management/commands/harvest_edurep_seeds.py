from collections import defaultdict

from django.utils.timezone import now

from datagrowth.resources.http.tasks import send
from datagrowth.configuration import create_config
from pol_harvester.management.base import HarvesterCommand
from pol_harvester.constants import HarvestStages
from edurep.models import EdurepHarvest


class Command(HarvesterCommand):

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('-f', '--freeze', type=str, required=True)
        parser.add_argument('-d', '--dummy', action="store_true", default=False)

    def handle(self, *args, **options):

        freeze_name = options["freeze"]
        dummy = options["dummy"]

        harvest_queryset = EdurepHarvest.objects.filter(
            freeze__name=freeze_name,
            stage=HarvestStages.NEW
        )
        if not harvest_queryset.exists():
            raise EdurepHarvest.DoesNotExist(
                f"There are no NEW EdurepHarvest objects for '{freeze_name}'"
            )

        self.header("EDUREP SEEDS HARVEST", options)

        # Calling the Edurep OAI-PMH interface and get the Edurep meta data about learning materials
        self.info("Fetching metadata for sources ...")
        send_config = create_config("http_resource", {
            "resource": "edurep.EdurepOAIPMH",
            "continuation_limit": 1000,
        })
        current_time = now()
        successes = defaultdict(int)
        fails = defaultdict(int)
        for harvest in self.progress(harvest_queryset, total=harvest_queryset.count()):
            set_specification = harvest.source.collection_name
            scc, err = send(set_specification, f"{harvest.latest_update_at:%Y-%m-%d}", config=send_config, method="get")
            successes[set_specification] += len(scc)
            fails[set_specification] += len(err)
            if not dummy:
                harvest.harvested_at = current_time
                harvest.save()
        self.info('Failed OAI-PMH calls: ', fails)
        self.info('Successful OAI-PMH calls: ', successes)
        success_count = sum(successes.values())
        fail_count = sum(fails.values())
        return f'OAI-PMH: {success_count}/{success_count+fail_count}'
