import logging
import json

from django.core.management.base import BaseCommand

from pol_harvester.utils.logging import log_header
from pol_harvester.readers.library4learning import WurLibrary4Learning


out = logging.getLogger("freeze")


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-i', '--input', type=str, required=True)
        parser.add_argument('-o', '--output', type=str, required=True)

    def handle(self, *args, **options):

        log_header(out, "LIBRARY 4 LEARNING XML EXTRACTION", options)

        wur = WurLibrary4Learning(options["input"])

        # Write to disk when output file is given
        output_file = options.get("output", None)
        if not output_file:
            return
        with open(output_file, "w") as json_file:
            json.dump(list(wur), json_file, indent=4)
