import logging
import json

from django.core.management.base import BaseCommand

from datagrowth.resources.http.tasks import send_serie
from pol_harvester.utils.logging import log_header
from ims.models import CommonCartridge
from edurep.models import EdurepFile


out = logging.getLogger("freeze")


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-i', '--input', type=str, required=True)

    def handle(self, *args, **options):

        log_header(out, "EDUREP DOWNLOAD IMSCC/IMSCP", options)

        with open(options["input"], "r") as json_file:
            records = json.load(json_file)

        config = {
            "resource": "edurep.EdurepFile",
            "_namespace": "http_resource",
            "_private": ["_private", "_namespace", "_defaults"]
        }
        package_records = [record for record in records if record["mime_type"] == "application/x-Wikiwijs-Arrangement"]

        successes, errors = send_serie(
            [[record["url"] + "?p=imscp"] for record in package_records],
            [{} for _ in records],
            config=config,
            method="get"
        )

        out.info("Errors while downloading IMSCP's: {}".format(len(errors)))

        create_count = 0
        get_count = 0
        for success_id in successes:
            edurep_file = EdurepFile.objects.get(id=success_id)
            common_cartridge, created = CommonCartridge.objects.get_or_create(file=edurep_file.body)
            if created:
                common_cartridge.clean()
                common_cartridge.save()
                create_count += 1
            else:
                get_count += 1

        out.info("IMSCP's downloaded: {}".format(len(successes)))
        out.info("IMSCP's converted to IMSCC: {}".format(create_count))
        out.info("IMSCP's previously converted to IMSCC: {}".format(get_count))
