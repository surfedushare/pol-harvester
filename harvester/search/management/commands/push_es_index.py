import logging
from collections import defaultdict

from django.conf import settings
from django.core.management.base import BaseCommand

from pol_harvester.constants import HarvestStages
from pol_harvester.models import Freeze, Arrangement
from edurep.models import EdurepHarvest
from search.models import ElasticIndex
from search.utils.elastic import get_index_config


log = logging.getLogger("freeze")


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-f', '--freeze', type=str, required=True)
        parser.add_argument('-r', '--recreate', action="store_true")
        parser.add_argument('-p', '--promote', action="store_true")

    def handle(self, *args, **options):

        freeze = Freeze.objects.get(name=options["freeze"])
        recreate = options["recreate"]
        promote = options["promote"]
        earliest_harvest = freeze.get_earliest_harvest_date()

        print(f"Upserting ES index for {freeze.name}")
        print(f"since:{earliest_harvest:%Y-%m-%d}, recreate:{recreate} and promote:{promote}")

        lang_doc_dict = freeze.get_elastic_documents_by_language(since=earliest_harvest)
        for lang in lang_doc_dict.keys():
            log.info(f'{lang}:{len(lang_doc_dict[lang])}')

        for lang, docs in lang_doc_dict.items():
            if lang not in settings.ELASTIC_SEARCH_ANALYSERS:
                continue
            config = get_index_config(lang)
            index, created = ElasticIndex.objects.get_or_create(
                name=freeze.name,
                language=lang,
                defaults={
                    "freeze": freeze,
                    "configuration": config
                }
            )
            index.clean()
            index.push(docs, recreate=recreate)
            index.save()
            if promote or recreate:
                print(f"Promoting index { index.remote_name } to latest")
                index.promote_to_latest()
            log.info(f'{lang} errors:{index.error_count}')
