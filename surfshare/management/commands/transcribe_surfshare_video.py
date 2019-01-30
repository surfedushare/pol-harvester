import os
import logging
from tqdm import tqdm
import json
from urlobject import URLObject

from django.core.management.base import BaseCommand

from datagrowth.configuration import create_config
from datagrowth.resources.shell.tasks import run
from datagrowth.exceptions import DGShellError
from pol_harvester.models import YouTubeDLResource
from pol_harvester.utils.language import get_kaldi_model_from_snippet
from surfshare.constants import VIDEO_DOMAINS


log = logging.getLogger(__name__)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-i', '--input', type=str, required=True)

    def handle(self, *args, **options):

        video_sources = []
        for path, dirs, files in os.walk(options["input"]):
            for file in files:
                with open(os.path.join(path, file)) as json_file:
                    data = json.load(json_file)
                    for document in data.get("documents", []):
                        url = URLObject(document["url"])
                        if url.hostname not in VIDEO_DOMAINS:
                            continue
                        if "youtube.com" in url.hostname:
                            url = url.del_query_param('list')
                            url = url.del_query_param('index')
                        data["url"] = str(url)
                        video_sources.append(data)

        for video_source in tqdm(video_sources):
            video_url = video_source["url"]
            try:
                download = YouTubeDLResource().run(video_url)
            except DGShellError:
                continue
            if not download.success:
                continue
            _, file_paths = download.content
            if not file_paths:
                log.warning("Could not find download(s) for: {}".format(video_source["id"]))
                continue
            title = video_source.get("title", None)
            kaldi_model = get_kaldi_model_from_snippet(title)
            if kaldi_model is None:
                log.warning("Unknown language for: {}".format(video_source["id"]))
                continue
            config = create_config("shell_resource", {
                "resource": kaldi_model
            })
            for file_path in file_paths:
                run(file_path, config=config)
