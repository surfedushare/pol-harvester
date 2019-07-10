import os
import logging
import matplotlib.pyplot as plt
import json
import numpy as np

from datagrowth import settings as datagrowth_settings
from pol_harvester.models import Freeze, Annotation, KaldiNLResource
from pol_harvester.management.base import OutputCommand, FreezeCommand
from pol_harvester.utils.word_error_rates import wer, cleanstring
from edurep.constants import HBOVPK_TEST_REFERENCES


out = logging.getLogger("freeze")


class Command(FreezeCommand, OutputCommand):

    def add_arguments(self, parser):
        parser.add_argument('references', nargs='*', type=str)
        parser.add_argument('-f', '--freeze', type=str, required=True)
        parser.add_argument('-c', '--collection', type=str)
        parser.add_argument('--hbovpk', action="store_true")

    def compare_transcripts_by_references(self, references, freeze):
        wers = {}
        for annotation in Annotation.objects.filter(reference__in=references, name="video_plain_text").order_by("id"):
            if not annotation.annotation:
                continue
            doc = freeze.documents.filter(reference=annotation.reference).last()  # TODO: use .get() after GH-48
            if not doc.properties["text"]:
                continue
            gold = cleanstring(annotation.annotation)
            hypothesis = cleanstring(doc.properties["text"])
            wers[annotation.reference] = wer(gold, hypothesis)
        return wers

    def compare_transcripts_by_resources(self, references):
        wers = {}
        for annotation in Annotation.objects.filter(reference__in=references, name="video_plain_text").order_by("id"):
            resource = KaldiNLResource.objects.get(config__contains=annotation.reference)
            content_type, text = resource.content
            gold = cleanstring(annotation.annotation)
            hypothesis = cleanstring(text)
            wers[annotation.reference] = wer(gold, hypothesis)
        return wers

    def handle(self, *args, **options):

        freeze = Freeze.objects.get(name=options["freeze"])
        is_hbovpk = options["hbovpk"]
        references = options["references"]
        if not references and not is_hbovpk:
            references = freeze.documents.all().values_list("reference", flat=True)

        assert not is_hbovpk or not len(references), "Expected to use references from HBOVPK instead of input/freeze"

        if is_hbovpk:
            references = HBOVPK_TEST_REFERENCES

        wers = self.compare_transcripts_by_references(references, freeze)

        if not is_hbovpk:
            wer_values = [int(value*100) for value in wers.values() if value <= 1]
            print(len(wer_values))
            print(np.mean(wer_values))
            fig, ax = plt.subplots()
            analysis_directory = os.path.join(datagrowth_settings.DATAGROWTH_DATA_DIR, freeze.name)
            os.makedirs(analysis_directory, exist_ok=True)
            ax.hist(wer_values, bins=range(0, 100, 5))
            fig.savefig(os.path.join(analysis_directory, "wer-histogram.png"))
            return

        print(json.dumps(wers, indent=4))
        print("*"*100)
        print(json.dumps(self.compare_transcripts_by_resources(references), indent=4))
