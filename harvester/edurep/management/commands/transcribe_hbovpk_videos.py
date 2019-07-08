import os
from tqdm import tqdm

from datagrowth.configuration import create_config
from datagrowth.resources.shell.tasks import run
from datagrowth.exceptions import DGShellError
from pol_harvester.models import Freeze, YouTubeDLResource
from pol_harvester.management.base import OutputCommand, FreezeCommand


REFERENCES = [
    "063b9b2562578274d47579025a9cf15483bf5732",
    "3d745e7adde31354c12f15c55f2e2a805bb6de3b",
    "3fb1ec3dfb37004ce6e5d0e3a4c66962ab7f1836",
    "47400bd9de5920a96b461433734ed5379a53da3d",
    "6f6ae1d8cd6a2cc541620ded919f9f317466cdd5",
    "ea3cc3dbf6b9309b3f35f102bf0e3094ee85bba1",
    "f3efd1a94f3212de77a450f3c5aaf4ab38fc97c8"
]


class Command(FreezeCommand, OutputCommand):

    def add_arguments(self, parser):
        parser.add_argument('-f', '--freeze', type=str, required=True)

    def handle(self, *args, **options):

        freeze = Freeze.objects.get(name=options["freeze"])

        videos = [(doc.reference, doc.properties["url"],) for doc in freeze.documents.filter(reference__in=REFERENCES)]
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
