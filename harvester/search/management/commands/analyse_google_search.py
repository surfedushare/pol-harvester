import requests

from django.core.management import BaseCommand
from django.contrib.auth.models import User

from datagrowth.exceptions import DGHttpWarning204
from pol_harvester.models import Freeze
from search.models import GoogleText, Query
from search.utils.metrics import dcg_at_k


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-u', '--username', type=str, required=True)
        parser.add_argument('-f', '--freeze', type=str, required=True)

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

        user = User.objects.get(username=options["username"])
        freeze = Freeze.objects.get(name=options["freeze"])

        for query, ranking in Query.objects.get_query_rankings(user=user, freeze=freeze).items():
            query_text = query.query
            print(query_text)
            print("-" * len(query_text))
            results = GoogleText()
            try:
                results = results.get(query_text)
                results.close()
            except DGHttpWarning204:
                print(f"WARNING: no Google search results for '{query_text}'")
            self.evaluate_google_results(results, ranking)
            print()
            print()
