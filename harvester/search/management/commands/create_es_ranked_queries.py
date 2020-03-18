import os
import json
import logging
from copy import copy
from itertools import chain, combinations_with_replacement
import requests
from datetime import datetime

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from datagrowth import settings as datagrowth_settings
from pol_harvester.models import Freeze
from search.models import QueryRanking, Query
from search.utils.elastic import get_es_config


log = logging.getLogger("freeze")


METRICS = {
    'precision': {
        'relevant_rating_threshold': 4,
        'ignore_unlabeled': False
    },
    'mean_reciprocal_rank': {
        'relevant_rating_threshold': 4
    },
    'dcg': {
        'normalize': True
    },
    'expected_reciprocal_rank': {
        'maximum_relevance': 5
    }
}


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-u', '--username', type=str, required=True)
        parser.add_argument('-f', '--freeze', type=str, required=True)
        parser.add_argument('-m', '--metrics', nargs="*", default=METRICS.keys())
        parser.add_argument('-k', '--result-count', type=int, default=20)
        parser.add_argument('--fields', nargs="+", default=[
            'title^2', 'text', 'text_plain', 'title_plain', 'keywords', 'description', 'description_plain'
        ])

    def handle(self, *args, **options):

        metrics = options["metrics"]
        user = User.objects.get(username=options["username"])
        freeze = Freeze.objects.get(name=options["freeze"])
        if not QueryRanking.objects.filter(user=user, freeze=freeze).exists():
            print(f"Query rankings by {user.username} for {freeze.name} do not exist")
            return

        indices = freeze.get_elastic_indices()
        field_combinations = sorted(set([
            tuple(sorted(set(combo)))
            for combo in combinations_with_replacement(options["fields"], len(options["fields"]))
        ]))
        today = datetime.today()
        freeze_folder = os.path.join(
            datagrowth_settings.DATAGROWTH_DATA_DIR,
            "elastic",
            freeze.name,
            f"{today:%Y-%m-%d}"
        )
        os.makedirs(freeze_folder, exist_ok=True)

        for metric_name in metrics:

            metric = copy(METRICS[metric_name])
            metric["k"] = options["result_count"]
            results = {}

            for fields in field_combinations:
                body = {
                    'requests': list(
                        chain(
                            query.get_elastic_ranking_request(freeze, user, fields)
                            for query in Query.objects.filter(users=user)
                        )
                    ),
                    'metric': {metric_name: metric}
                }
                endpoint, auth, _ = get_es_config()
                result = requests.get(
                    '{}/{}/_rank_eval'.format(endpoint, indices),
                    auth=auth,
                    json=body
                )
                response = json.loads(result.text)
                results["|".join(fields)] = {
                    query: response["details"][query]["metric_score"]
                    for query in response["details"].keys()
                }

            output_file = f"{metric_name}.{user.id}.json"
            output = {
                "freeze": freeze.name,
                "user": user.username,
                "queries": results
            }
            with open(os.path.join(freeze_folder, output_file), 'w+t') as file:
                json.dump(output, file)
