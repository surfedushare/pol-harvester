import logging
from collections import defaultdict

from django.conf import settings
from django.core.management.base import BaseCommand

from pol_harvester.models import Freeze, Arrangement
from search.models import ElasticIndex
from search.utils.elastic import get_index_config


log = logging.getLogger("freeze")


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-f', '--freeze', type=str, required=True)
        parser.add_argument('-r', '--recreate', action="store_true")

    def handle(self, *args, **options):

        freeze = Freeze.objects.get(name=options["freeze"])
        recreate = options["recreate"]
        arrangements = Arrangement.objects.filter(freeze=freeze)
        print(f"Creating freeze { freeze.name } index recreate:{recreate} and arrangement count:{len(arrangements)}")

        lang_doc = []
        for arrangement in arrangements:
            for dictionary in arrangement.to_documents():
                lang_doc.append((dictionary["language"], dictionary,))

        lang_doc_dict = defaultdict(list)
        # create a list so we can report counts
        for lang, doc in lang_doc:
            lang_doc_dict[lang].append(doc)
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
            log.info(f'{lang} errors:{index.error_count}')
