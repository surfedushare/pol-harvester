import requests

from django.core.management import BaseCommand

from datagrowth.exceptions import DGHttpWarning204
from search.models import GoogleText
from search.utils.metrics import dcg_at_k
from search.utils.rankings import yield_query_rankings


class Command(BaseCommand):

    def evaluate_google_results(self, results, ranking):

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

        for query, ranking in yield_query_rankings():

            print(query)
            print("-" * len(query))
            results = GoogleText()
            try:
                results = results.get(query)
                results.close()
            except DGHttpWarning204:
                print(f"WARNING: no Google search results for '{query}'")
            self.evaluate_google_results(results, ranking)
            print()
            print()
