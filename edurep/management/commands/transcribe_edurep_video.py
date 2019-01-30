import logging
import os
from tqdm import tqdm
import json
from urlobject import URLObject

from django.core.management.base import BaseCommand

from datagrowth.configuration import create_config
from datagrowth.resources.shell.tasks import run
from datagrowth.exceptions import DGShellError
from pol_harvester.models import YouTubeDLResource
from pol_harvester.utils.language import get_kaldi_model_from_snippet
from edurep.constants import VIDEO_DOMAINS


log = logging.getLogger(__name__)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-i', '--input', type=str, required=True)

    def handle(self, *args, **options):

        with open(options["input"], "r") as json_file:
            records = json.load(json_file)

        video_records = []
        for record in records:
            url = URLObject(record["source"])
            if not url.hostname in VIDEO_DOMAINS:
                continue
            if "youtube.com" in url.hostname:
                url = url.del_query_param('list')
                url = url.del_query_param('index')
            record["source"] = str(url)
            video_records.append(record)

        for video_record in tqdm(video_records):
            try:
                download = YouTubeDLResource().run(video_record["source"])
            except DGShellError:
                continue
            _, file_paths = download.content
            if not len(file_paths):
                log.warning("Could not find download for: {}".format(video_record["source"]))
                continue
            title = video_record.get("title", None)
            kaldi_model = get_kaldi_model_from_snippet(title)
            if kaldi_model is None:
                log.warning("Unknown language for: {}".format(video_record["id"]))
                continue
            config = create_config("shell_resource", {
                "resource": kaldi_model
            })
            for file_path in file_paths:
                if not os.path.exists(file_path):
                    log.warning("Path does not exist:", file_path)
                run(file_path, config=config)
