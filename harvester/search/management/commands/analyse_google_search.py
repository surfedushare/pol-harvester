import os
import json
from collections import OrderedDict
import requests
from itertools import chain

from django.core.management import BaseCommand

from datagrowth.exceptions import DGHttpWarning204
from search.models import GoogleText
from search.rank_metrics import dcg_at_k


class Command(BaseCommand):

    def evaluate_google_results(self, query, results, ranking):

        ratings = []
        content_type, data = results.content
        if not data:
            print([])
            print(0)
            return

        for item in data["items"]:
            print(item["link"])
            api_url = item["link"].replace("content/documents", "api/v1/document")
            api_url = api_url.replace("https://surfpol.nl", "http://localhost:8000")
            response = requests.get(api_url)
            doc = response.json()
            rating = ranking[doc["reference"]] if doc["reference"] in ranking else 0
            ratings.append(rating)

        print(ratings)
        print(dcg_at_k(ratings, 10))

    def handle(self, *args, **options):
        with open(os.path.join("..", "data", "queries", "queries-en.json")) as en_queries_file:
            en_queries = json.load(en_queries_file)
        with open(os.path.join("..", "data", "queries", "queries-nl.json")) as nl_queries_file:
            nl_queries = json.load(nl_queries_file)

        for query_info in chain(nl_queries, en_queries):
            query = query_info["queries"][0]

            print(query)
            print("-" * len(query))

            sorted_items = sorted(
                ((item["hash"], item["rating"],) for item in query_info["items"]),
                key=lambda item: item[1],
                reverse=True  # TODO: check if higher is indeed better, it's required for the metric it seems
            )
            ranking = OrderedDict(sorted_items)

            results = GoogleText()
            try:
                results = results.get(query)
                results.close()
            except DGHttpWarning204:
                print(f"WARNING: no Google search results for '{query}'")

            self.evaluate_google_results(query, results, ranking)
            print()
            print()
