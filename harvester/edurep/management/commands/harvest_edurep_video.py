import os
from collections import defaultdict

from datagrowth.configuration import create_config
from datagrowth.resources.shell.tasks import run_serie

from pol_harvester.management.base import HarvesterCommand
from pol_harvester.models import YouTubeDLResource
from pol_harvester.constants import HarvestStages
from pol_harvester.utils.language import get_kaldi_model_from_snippet
from pol_harvester.utils.logging import log_header
from edurep.models import EdurepHarvest
from edurep.utils import get_edurep_oaipmh_seeds, get_edurep_basic_resources


class Command(HarvesterCommand):

    def add_arguments(self, parser):
        parser.add_argument('-f', '--freeze', type=str, required=True)
        parser.add_argument('-d', '--dummy', action="store_true")

    def finish(self, harvest_queryset):
        for harvest in harvest_queryset:
            harvest.stage = HarvestStages.VIDEO
            harvest.save()

    def filter_video_seeds(self, seeds):
        video_seeds = {}
        for seed in self.progress(seeds):
            file_resource, tika_resource = get_edurep_basic_resources(seed["url"])
            if tika_resource is not None and tika_resource.has_video():
                video_seeds[seed["url"]] = seed
        return video_seeds

    def download_seed_videos(self, video_seeds):
        config = create_config("http_resource", {
            "resource": "pol_harvester.YouTubeDLResource"
        })
        return run_serie(  # TODO: make this parallel
            self.progress([
                [seed["url"]] for seed in video_seeds
            ]),
            [
                {} for _ in video_seeds
            ],
            config=config
        )

    def transcribe_video_resources(self, video_download_ids, seeds):
        no_paths_count, invalid_paths_count, success_count, error_count = 0, 0, 0, 0
        kaldi_file_paths = defaultdict(list)
        # Preprocess the videos
        for video_download_resource in YouTubeDLResource.objects.filter(id__in=video_download_ids, status=0):
            # Make sure that the video has a valid audio file
            _, file_paths = video_download_resource.content
            if not len(file_paths):
                no_paths_count += 1
                continue
            file_path = file_paths[0]
            if not os.path.exists(file_path):
                invalid_paths_count += 1
                continue
            # Try to transcribe the file based on metadata
            video_url = video_download_resource.variables()["url"]
            # TODO: determine Kaldi through meta data
            # It's possible to pass the URL through get_edurep_basic_resources
            # With the Tika and File resources it's much easier to determine a proper language
            seed = seeds[video_url]
            title = seed.get("title", None)
            kaldi_model = get_kaldi_model_from_snippet(title)
            kaldi_file_paths[kaldi_model].append(file_paths[0])
        no_language_count = len(kaldi_file_paths.pop(None, []))
        # Actual transcribing
        for kaldi_model, paths in kaldi_file_paths.items():
            config = create_config("shell_resource", {
                "resource": kaldi_model
            })
            sccs, errs = run_serie(
                self.progress([
                    [path] for path in paths
                ]),
                [
                    {} for _ in paths
                ],
                config=config
            )
            success_count += len(sccs)
            error_count += len(errs)
        return no_paths_count, invalid_paths_count, no_language_count, success_count, error_count

    def handle(self, *args, **options):

        freeze_name = options["freeze"]
        is_dummy = options["dummy"]

        harvest_queryset = EdurepHarvest.objects.filter(
            freeze__name=freeze_name,
            stage=HarvestStages.BASIC
        )
        if not harvest_queryset.exists():
            raise EdurepHarvest.DoesNotExist(
                f"There are no scheduled and BASIC EdurepHarvest objects for '{freeze_name}'"
            )

        self.header("HARVEST EDUREP VIDEO", options)

        if is_dummy:
            self.info("Skipping command because dummy mode was specified")
            self.finish(harvest_queryset)
            return

        self.info("Extracting data from sources ...")
        seeds = []
        for harvest in self.progress(harvest_queryset, total=harvest_queryset.count()):
            set_specification = harvest.source.collection_name
            harvest_seeds = get_edurep_oaipmh_seeds(set_specification, harvest.latest_update_at, include_deleted=False)
            seeds += harvest_seeds
        self.info("Files considered for processing: {}".format(len(seeds)))

        self.info("Preparing video seeds ...")
        video_seeds = self.filter_video_seeds(seeds)
        self.info("Total videos: {}".format(len(video_seeds)))

        self.info("Downloading videos ...")
        download_scc, download_err = self.download_seed_videos(video_seeds.values())
        self.info("Errors while downloading audio from videos: {}".format(len(download_err)))
        self.info("Audio downloaded successfully: {}".format(len(download_scc)))

        self.info("Transcribing videos ...")
        no_paths_count, invalid_paths_count, no_language_count, success_count, error_count = \
            self.transcribe_video_resources(download_scc, video_seeds)
        self.info("Skipped video content due to missing audio file: {}".format(no_paths_count + invalid_paths_count))
        self.info("Skipped video content due to unknown language: {}".format(no_language_count))
        self.info("Errors while transcribing videos: {}".format(error_count))
        self.info("Videos transcribed successfully: {}".format(success_count))

        self.finish(harvest_queryset)
