import os
import json
import logging
from copy import copy
from itertools import chain
import requests

from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from datagrowth import settings as datagrowth_settings
from pol_harvester.models import Freeze
from search.models import QueryRanking
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


def get_query(query, fields):
    return {
        'bool': {
            'must': [
                {
                    "multi_match": {
                        "fields": fields,
                        "fuzziness": 0,
                        "operator": "or",
                        "query": query,
                        "type": "best_fields",
                        "tie_breaker": 0.3
                    }
                }
            ],
            'should': [
                {
                    "multi_match": {
                        "fields": fields,
                        "query": query,
                        "type": "phrase"
                    }
                }
            ]
        }
    }


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-u', '--username', type=str, required=True)
        parser.add_argument('-f', '--freeze', type=str, required=True)
        parser.add_argument('-m', '--metrics', nargs="*", default=METRICS.keys())
        parser.add_argument('-k', '--result-count', type=int, default=20)
        parser.add_argument('--fields', nargs="+", default=['title^2', 'text', 'text_plain', 'title_plain'])

    def handle(self, *args, **options):

        metrics = options["metrics"]
        user = User.objects.get(username=options["username"])
        freeze = Freeze.objects.get(name=options["freeze"])
        indices = ",".join([index.remote_name for index in freeze.indices.all()])
        fields = options["fields"]
        output_folder = os.path.join(datagrowth_settings.DATAGROWTH_DATA_DIR, "elastic", freeze.name, user.username)

        for metric_name in metrics:

            metric = copy(METRICS[metric_name])
            metric["k"] = options["result_count"]

            body = {
                'requests': list(
                    chain(
                        ranking.get_elastic_ranking_request(get_query(ranking.query.query, fields))
                        for ranking in QueryRanking.objects.filter(user=user, freeze=freeze)
                    )
                ),
                'metric': {metric_name: metric}
            }

            print(json.dumps(body, indent=4))
            break  # TODO: make actual calls

            endpoint, auth, _ = get_es_config()
            result = requests.get(
                '{}/{}/_rank_eval'.format(endpoint, indices),
                auth=auth,
                json=body
            )
            results = json.loads(result.text)
            with open(os.path.join(output_folder, f'{indices}_{metric_name}.json'), 'w+t') as file:
                json.dump(results, file)
            print(f'{metric_name:<27}: {results["metric_score"]:>20}')

        # TODO: remove debug output
        print(indices)
        print(output_folder)
