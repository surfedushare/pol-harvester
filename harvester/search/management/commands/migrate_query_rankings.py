import logging

from django.core.management.base import BaseCommand

from search.models import QueryRanking


log = logging.getLogger("freeze")


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-f', '--from', type=str, required=True)
        parser.add_argument('-t', '--to', type=str, required=True)
        parser.add_argument('-r', '--recreate', action="store_true")

    def handle(self, *args, **options):

        from_index = options["from"]
        to_index = options["to"]

        print(f"Migrating queries from {from_index} to {to_index}")

        unknown_indices = set()
        migrate_count = 0
        for query_ranking in QueryRanking.objects.all():

            migrated_ranking = {}
            for identifier, ranking in query_ranking.ranking.items():
                index, doc_id = identifier.split(":")
                if index != from_index and index != to_index:
                    unknown_indices.add(index)
                    break
                elif index != from_index:
                    break
                migrated_ranking[f"{to_index}:{doc_id}"] = ranking

            if migrated_ranking:
                migrate_count += 1
                query_ranking.ranking = migrated_ranking
                query_ranking.save()

        print("Unknown indices:", unknown_indices)
        print("Migrate count:", migrate_count)
