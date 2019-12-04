import logging

from django.core.management.base import BaseCommand

from pol_harvester.models import Document
from search.models import QueryRanking


log = logging.getLogger("freeze")


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-f', '--freeze', type=str, required=True)

    def handle(self, *args, **options):

        freeze_name = options["freeze"]

        print(f"Deleting non-video query rankings from freeze {freeze_name}")

        keep_count = 0
        remove_count = 0
        for query_ranking in QueryRanking.objects.filter(freeze__name=freeze_name):

            migrated_ranking = {}
            for identifier, ranking in query_ranking.ranking.items():
                index, doc_id = identifier.split(":")
                if not Document.objects.filter(reference=doc_id, properties__file_type="video").exists():
                    remove_count += 1
                    continue
                keep_count += 1
                migrated_ranking[f"{index}:{doc_id}"] = ranking

            if migrated_ranking:
                query_ranking.ranking = migrated_ranking
                query_ranking.save()

        print(f"Keep count: {keep_count}")
        print(f"Remove count: {remove_count}")
