import os

from django.core.management.base import BaseCommand

from pol_harvester.models import KaldiAspireResource


class Command(BaseCommand):

    def handle(self, *args, **options):
        video_directory = '/mnt/videos/'
        for entry in os.scandir(video_directory):
            if not entry.is_file():
                continue
            kaldi = KaldiAspireResource().run(entry.path)
            kaldi.save()
