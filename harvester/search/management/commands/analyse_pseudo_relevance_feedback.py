from django.core.management import BaseCommand
from django.contrib.auth.models import User

from pol_harvester.models import Freeze
from search.models import Query
from search.utils.elastic import get_es_client
from search.utils.metrics import dcg_at_k


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-u', '--username', type=str, required=True)
        parser.add_argument('-f', '--freeze', type=str, required=True)
        parser.add_argument('--fields', nargs="+", default=['title^2', 'text', 'text_plain', 'title_plain', 'keywords'])

    def evaluate_elastic_results(self, results, ranking):

        ratings = []

        for item in results["hits"]["hits"]:
            print(item["_id"])

            rating = ranking[item["_id"]] if item["_id"] in ranking else 0
            ratings.append(rating)

        print(ratings)
        print(dcg_at_k(ratings, 10))

    def handle(self, *args, **options):

        user = User.objects.get(username=options["username"])
        freeze = Freeze.objects.get(name=options["freeze"])

        indices = freeze.get_elastic_indices()
        es_client = get_es_client()
        vectorizer = freeze.get_tfidf_vectorizer()
        top_k = 3

        if vectorizer is None:
            raise RuntimeError("Could not get vectorizer for freeze. Is it created?")

        for query, ranking in Query.objects.get_query_rankings(freeze=freeze, user=user).items():

            query_text = query.query
            print(query_text)
            print("-" * len(query_text))

            pre_results = es_client.search(
                index=indices,
                body={"query": query.get_elastic_query_body(options["fields"])}
            )

            # Prints results for the original query
            self.evaluate_elastic_results(pre_results, ranking)
            print("-" * len(query_text))

            # Now we enrich the query with top k tfidf terms
            tfidf_top_results = vectorizer.transform(
                [hit["_source"]["text"] for hit in pre_results["hits"]["hits"] if hit["_source"]["text"]]
            )
            tfidf_words = tfidf_top_results.sum(axis=0)
            tfidf_top_indices = tfidf_words.A1.argsort()[-1*top_k:]
            feature_names = vectorizer.get_feature_names()
            enrichment = [feature_names[ix] for ix in tfidf_top_indices]
            print(enrichment)

            # Perform new query and evaluate
            results = es_client.search(
                index=indices,
                body={"query": query.get_elastic_query_body(options["fields"], enrichment)}
            )
            self.evaluate_elastic_results(results, ranking)

            print()
            print()
