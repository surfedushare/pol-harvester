from collections import defaultdict

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

        print("Result ids:")
        for item in results["hits"]["hits"]:
            print("- ", item["_id"])

            rating = ranking[item["_id"]] if item["_id"] in ranking else 0
            ratings.append(rating)

        print()
        print("Ratings of results:", ratings)
        print("DCG:", dcg_at_k(ratings, 10))

    def handle(self, *args, **options):

        user = User.objects.get(username=options["username"])
        freeze = Freeze.objects.get(name=options["freeze"])

        indices = freeze.get_elastic_indices()
        es_client = get_es_client()
        top_k_hits = 5
        top_k_words = 3

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
            print("*" * len(query_text))

            # Now we enrich the query with top k tfidf terms
            enrichments = []
            language_hits = defaultdict(list)
            for hit in pre_results["hits"]["hits"]:
                if not hit["_source"]["text"]:
                    continue
                language_hits[hit["_source"]["language"]].append(hit)
            for language, hits in language_hits.items():
                vectorizer = freeze.get_tfidf_vectorizer(language)
                if vectorizer is None:
                    raise RuntimeError("Could not get {language} vectorizer for freeze. Is it created?")
                tfidf_top_results = vectorizer.transform([hit["_source"]["text"] for hit in hits[:top_k_hits]])
                tfidf_words = tfidf_top_results.sum(axis=0)
                tfidf_top_indices = tfidf_words.A1.argsort()[-1*top_k_words*top_k_words:]
                feature_names = vectorizer.get_feature_names()
                enrichments += [
                    (feature_names[ix], tfidf_words.A1[ix],) for ix in tfidf_top_indices
                    if feature_names[ix] not in query_text
                ]
            enrichments = sorted(enrichments, key=lambda item: item[1], reverse=True)[:top_k_words]
            enrichments = [enrichment[0] for enrichment in enrichments]
            print("Applied enrichments:", enrichments)

            # Perform new query and evaluate
            results = es_client.search(
                index=indices,
                body={"query": query.get_elastic_query_body(options["fields"], enrichments)}
            )
            self.evaluate_elastic_results(results, ranking)

            print()
            print()
