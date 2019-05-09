import logging
import os
import json
import pandas as pd
from tqdm import tqdm

from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage

from datagrowth.resources.http.tasks import send_serie
from pol_harvester.utils.logging import log_header
from ims.models import CommonCartridge
from edurep.models import EdurepFile


out = logging.getLogger("freeze")


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-i', '--input', type=str, required=True)

    def handle(self, *args, **options):

        log_header(out, "EDUREP EXTRACT IMSCC", options)

        with open(options["input"], "r") as json_file:
            records = json.load(json_file)

        df = pd.DataFrame(records)
        df = df.loc[df['mime_type']=="application/x-Wikiwijs-Arrangement"]
        uris = [EdurepFile.uri_from_url(url + "?p=imscp") for url in list(df["url"])]
        file_resources = list(EdurepFile.objects.filter(uri__in=uris))
        file_paths = [edurep_file.body.replace(default_storage.base_location, "") for edurep_file in file_resources]
        imscc_cartridges = list(CommonCartridge.objects.filter(file__in=file_paths))

        files = []
        skipped = 0
        for cartridge in tqdm(imscc_cartridges):
            cartridge.extract()
            resources = cartridge.get_resources().values()
            destination = cartridge.get_extract_destination()
            for resource in resources:
                if resource["content_type"] == "webcontent":
                    paths = [
                        os.path.join(destination, file)
                        for file in resource["files"]
                    ]
                    files += paths
                else:
                    skipped += 1

        config = {
            "resource": "pol_harvester.HttpTikaResource",
            "_namespace": "http_resource",
            "_private": ["_private", "_namespace", "_defaults"]
        }

        successes, errors = send_serie(
            [[] for _ in files],
            tqdm([{"file": file} for file in files]),
            config=config,
            method="post"
        )

        out.info("Skipped text extraction due to content_type restrictions: {}".format(skipped))
        out.info("Errors while extracting texts: {}".format(len(errors)))
        out.info("Texts extracted successfully: {}".format(len(successes)))
