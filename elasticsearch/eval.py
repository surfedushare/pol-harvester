#!/usr/bin/env python3
import json
import os
import re
from itertools import chain

import click
import requests
from toolz.dicttoolz import assoc

import core

METRICS = {
    'precision': {
        'relevant_rating_threshold': 1,
        'ignore_unlabeled': False
    },
    'mean_reciprocal_rank': {
        'relevant_rating_threshold': 1
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
    return [
        {
            "multi_match": {
                "fields": fields,
                "fuzziness": 0,
                "operator": "or",
                "query": query_text,
                "type": "best_fields"
            }
        },
        {
            "multi_match": {
                "fields": fields,
                "operator": "or",
                "query": query_text,
                "type": "phrase_prefix"
            }
        }
    ]


def format_requests(query, index, fields):
    requests = []
    for item in query['queries']:
        request = {
            'id': re.sub(r'\s+', '-', item),
            'request': {
                'query': {
                    'bool': {
                        'minimum_should_match': 1,
                        'should': format_multi_match(item, fields)
                    }
                }
            },
            'ratings': [
                {'_index': index, '_id': doc['hash'], 'rating': doc['rating']}
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
@click.argument('credentials', type=core.get_es_config)
@click.option('--metrics', multiple=True, default=METRICS.keys())
@click.option('--fields', multiple=True, default=['title^2', 'text'])
@click.option('-k', type=int, default=20, help='max. #documents per query')
def main(queries, index, metrics, credentials, k, fields):
    os.makedirs('evaluations', exist_ok=True)
    for metric in metrics:

        body = {
                'requests': list(chain(*[format_requests(_, index, fields) for _ in queries])),
            'metric': get_metric(metric, k)
        }
        endpoint, auth, _ = credentials
        result = requests.get(
            '{}/{}/_rank_eval'.format(endpoint, index),
            auth=auth,
            json=body
        )
        results = json.loads(result.text)
        with open(os.path.join(f'evaluations/{index}_{metric}.json'), 'wt') as f:
            json.dump(results, f)
        print(f'{metric:<27}: {results["metric_score"]:>20}')


if __name__ == '__main__':
    main()
