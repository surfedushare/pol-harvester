from django.core.management import call_command

from pol_harvester.models import Freeze
from pol_harvester.management.base import HarvesterCommand


class Command(HarvesterCommand):

    def handle(self, *args, **options):
        for freeze in Freeze.objects.filter(is_active=True):
            call_command("harvest_edurep_seeds", freeze=freeze.name)
            call_command("harvest_edurep_basic", freeze=freeze.name)
            call_command("harvest_edurep_video", freeze=freeze.name, dummy=True)
            call_command("freeze_edurep", freeze=freeze.name)
            call_command("push_es_index", freeze=freeze.name)
