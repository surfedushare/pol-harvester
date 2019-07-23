import os
from tqdm import tqdm

from datagrowth.configuration import create_config
from datagrowth.resources.shell.tasks import run
from datagrowth.exceptions import DGShellError
from pol_harvester.models import Freeze, YouTubeDLResource
from pol_harvester.management.base import OutputCommand, FreezeCommand
from edurep.constants import HBOVPK_TEST_REFERENCES




class Command(FreezeCommand, OutputCommand):

    def add_arguments(self, parser):
        parser.add_argument('-f', '--freeze', type=str, required=True)

    def handle(self, *args, **options):

        freeze = Freeze.objects.get(name=options["freeze"])

        videos = [
            (doc.reference, doc.properties["url"],)
            for doc in freeze.documents.filter(reference__in=HBOVPK_TEST_REFERENCES)
        ]
        successes = []
        errors = []

        for ref, url in tqdm(videos):
            try:
                download = YouTubeDLResource().run(url)
            except DGShellError:
                print("Download does not exist")
                continue
            if not download.success:
                print("Download error")
                continue
            _, file_paths = download.content
            if not len(file_paths):
                print("Download missing file in output")
                continue

            config = create_config("shell_resource", {
                "resource": "pol_harvester.kaldinlresource",
                "reference": ref
            })
            file_path = file_paths[0]
            if not os.path.exists(file_path):
                print("Download missing file")
                continue
            sccs, errs = run(file_path, config=config)
            successes += sccs
            errors += errs
