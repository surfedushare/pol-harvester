import logging
import os
import json
from tqdm import tqdm

from pol_harvester.models import Freeze, Collection, Annotation, KaldiNLResource
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

        for annotation in Annotation.objects.filter(reference__in=references, name="video_plain_text"):
            doc = freeze.documents.filter(reference=annotation.reference).last()  # TODO: use .get() after GH-48
            gold = cleanstring(annotation.annotation)
            hypothesis = cleanstring(doc.properties["text"])
            print(annotation.reference, wer(gold, hypothesis))

    def compare_transcripts_by_resources(self, references):

        for annotation in Annotation.objects.filter(reference__in=references, name="video_plain_text"):
            resource = KaldiNLResource.objects.get(config__contains=annotation.reference)
            content_type, text = resource.content
            gold = cleanstring(annotation.annotation)
            hypothesis = cleanstring(text)
            print(annotation.reference, wer(gold, hypothesis))

    def handle(self, *args, **options):

        freeze = Freeze.objects.get(name=options["freeze"])
        collection_name = options["collection"]
        is_hbovpk = options["hbovpk"]
        references = options["references"]
        if not references and collection_name:
            collection = Collection.objects.get(name=collection_name, freeze=freeze)
            references = collection.documents.all().values_list("reference", flat=True)

        assert not is_hbovpk or not len(references), "Expected to use references from HBOVPK instead of input/collection"

        if is_hbovpk:
            references = HBOVPK_TEST_REFERENCES

        self.compare_transcripts_by_references(references, freeze)

        if not is_hbovpk:
            return

        self.compare_transcripts_by_resources(references)
