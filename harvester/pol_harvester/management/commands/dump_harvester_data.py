import os

from django.core.management import base, call_command

from datagrowth.utils import get_dumps_path, object_to_disk, queryset_to_disk
from pol_harvester.models import Freeze


class Command(base.LabelCommand):

    def dump_resources(self):
        call_command("dump_resource", "edurep.EdurepOAIPMH")

    def handle_label(self, freeze_label, **options):

        freeze = Freeze.objects.get(name=freeze_label)

        destination = get_dumps_path(freeze)
        if not os.path.exists(destination):
            os.makedirs(destination)
        file_name = os.path.join(destination, "{}.{}.json".format(freeze.name, freeze.id))
        with open(file_name, "w") as json_file:
            object_to_disk(freeze, json_file)
            queryset_to_disk(freeze.edurepsource_set, json_file)
            queryset_to_disk(freeze.edurepharvest_set, json_file)
            queryset_to_disk(freeze.indices, json_file)
            queryset_to_disk(freeze.collection_set, json_file)
            queryset_to_disk(freeze.arrangement_set, json_file)
            queryset_to_disk(freeze.document_set, json_file)

        self.dump_resources()
