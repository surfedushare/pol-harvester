from django.core.management import call_command

from pol_harvester.models import Freeze
from pol_harvester.management.base import HarvesterCommand

from edurep.models import EdurepOAIPMH

class Command(HarvesterCommand):

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('-r', '--reset', action="store_true",
                            help="Resets the Freeze model to be empty and deletes all OAI-PMH data")

    def handle(self, *args, **options):

        for freeze in Freeze.objects.filter(is_active=True):

            if options["reset"]:
                EdurepOAIPMH.objects.all().delete()
                freeze.reset()

            call_command("harvest_edurep_seeds", freeze=freeze.name)
            call_command("harvest_edurep_basic", freeze=freeze.name)
            call_command("harvest_edurep_video", freeze=freeze.name, dummy=True)
            call_command("freeze_edurep", freeze=freeze.name)
            call_command("push_es_index", freeze=freeze.name)
