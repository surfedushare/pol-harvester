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


out = logging.getLogger("freeze")
err = logging.getLogger("pol_harvester")


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-i', '--input', type=str, required=True)

    def handle(self, *args, **options):

        video_sources = []
        skipped_mime_type = 0
        skipped_domain = 0
        for path, dirs, files in os.walk(options["input"]):
            for file in files:
                with open(os.path.join(path, file)) as json_file:
                    data = json.load(json_file)
                    for document in data.get("documents", []):
                        mime_type = document.get("content-type", None)  # NB: content-type is wrong legacy naming
                        if mime_type is None:
                            skipped_mime_type += 1
                        url = URLObject(document["url"])
                        if url.hostname not in VIDEO_DOMAINS:
                            if mime_type.startswith("video"):
                                skipped_domain += 1
                            continue
                        if "youtube.com" in url.hostname:
                            url = url.del_query_param('list')
                            url = url.del_query_param('index')
                        document["url"] = str(url)
                        video_sources.append(document)

        skipped_download = 0
        skipped_language = 0
        skipped_missing = 0
        successes = []
        errors = []
        for video_source in tqdm(video_sources):
            video_url = video_source["url"]
            try:
                download = YouTubeDLResource().run(video_url)
            except DGShellError:
                skipped_download += 1
                continue
            if not download.success:
                skipped_download += 1
                continue
            _, file_paths = download.content
            if not len(file_paths):
                skipped_download += 1
                err.warning("Could not find download(s) for: {}".format(video_source["title"]))
                continue
            title = video_source.get("title", None)
            kaldi_model = get_kaldi_model_from_snippet(title)
            if kaldi_model is None:
                skipped_language += 1
                err.warning("Unknown language for: {}".format(video_source["title"]))
                continue
            config = create_config("shell_resource", {
                "resource": kaldi_model
            })
            file_path = file_paths[0]
            if not os.path.exists(file_path):
                err.warning("Path does not exist: {}".format(file_path))
                skipped_missing += 1
                continue
            sccs, errs = run(file_path, config=config)
            successes += sccs
            errors += errs

        out.info("Skipped video content due to missing mime type: {}".format(skipped_mime_type))
        out.info("Skipped video content due to domain restrictions: {}".format(skipped_domain))
        out.info("Skipped video content due to download failure: {}".format(skipped_download))
        out.info("Skipped video content due to unknown language: {}".format(skipped_language))
        out.info("Skipped video content due to missing audio file: {}".format(skipped_missing))
        out.info("Errors while transcribing videos: {}".format(len(errors)))
        out.info("Videos transcribed successfully: {}".format(len(successes)))
