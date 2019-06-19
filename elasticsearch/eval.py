#!/usr/bin/env python3
import json
import os
import re
from itertools import chain

import click
import requests
from toolz.dicttoolz import assoc

from harvester.pol_harvester.utils.elastic_search import get_es_client, get_es_config

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


def load_json(path):
    with open(path) as stream:
        return json.load(stream)


def format_multi_match(query_text, fields):
    return


def format_requests(query, index, fields):
    requests = []
    for query_text in query['queries']:
        request = {
            'id': re.sub(r'\s+', '-', query_text),
            'request': {
                'query': {
                    'bool': {
                        'must': [
                            {
                                "multi_match": {
                                    "fields": fields,
                                    "fuzziness": 0,
                                    "operator": "or",
                                    "query": query_text,
                                    "type": "best_fields",
                                    "tie_breaker": 0.3
                                }
                            }
                        ],
                        'should': [
                            {
                                "multi_match": {
                                    "fields": fields,
                                    "query": query_text,
                                    "type": "phrase"
                                }
                            }
                        ]
                    }
                }
            },
            'ratings': [
                {
                    '_index': index,
                    '_id': doc['hash'],
                    'rating': doc['rating']
                }
                for doc in query['items']
            ]
        }
        requests.append(request)
    return requests


def get_metric(name, k):
    return {name: assoc(METRICS[name], 'k', k)}


@click.command()
@click.argument('queries', type=load_json)
@click.argument('index')
@click.argument('output_folder')
@click.option('--metrics', multiple=True, default=METRICS.keys())
@click.option('--fields', multiple=True, default=['title^2', 'text',
    'text_plain', 'title_plain'])
@click.option('-k', type=int, default=20, help='max. #documents per query')
def main(queries, index, metrics, output_folder, k, fields):
    os.makedirs(output_folder, exist_ok=True)
    for metric in metrics:

        body = {
            'requests': list(chain(*[format_requests(_, index, fields) for _ in queries])),
            'metric': get_metric(metric, k)
        }
        endpoint, auth, _ = get_es_config()
        result = requests.get(
            '{}/{}/_rank_eval'.format(endpoint, index),
            auth=auth,
            json=body
        )
        results = json.loads(result.text)
        with open(os.path.join(output_folder, f'{index}_{metric}.json'), 'w+t') as file:
            json.dump(results, file)
        print(f'{metric:<27}: {results["metric_score"]:>20}')


if __name__ == '__main__':
    main()
