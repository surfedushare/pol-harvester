import os
import mwparserfromhell
from sklearn.feature_extraction.text import CountVectorizer
import joblib

from django.core.management.base import BaseCommand

from datagrowth import settings as datagrowth_settings
from datagrowth.configuration import create_config
from datagrowth.resources.http.tasks import send
from datagrowth.processors.input.extraction import ExtractProcessor

from pol_harvester.models import Corpus, Article
from pol_harvester.models.wikipedia.categories import WikipediaCategoryMembers


class Command(BaseCommand):

    CATEGORY_NAMESPACES = {
        "en": "Category:",
        "nl": "Categorie:"
    }

    def add_arguments(self, parser):
        parser.add_argument('categories', nargs='+', type=str)
        parser.add_argument('-l', '--language', type=str)

    def get_corpus_name(self, categories, category_namespace):
        return

    def clean_text(self, text, category_namespace):
        lines = text.split("\n")
        return "\n".join([
            line.replace("thumb:", "").replace(category_namespace, "").replace(category_namespace.lower(), "")
            for line in lines
        ])

    def handle(self, *args, **options):

        language = options["language"]
        category_namespace = self.CATEGORY_NAMESPACES[language]
        categories = options["categories"]
        corpus_name = "-".join(sorted([category.replace(category_namespace, "") for category in categories]))

        results = []
        for category in categories:
            category_name = category.replace(category_namespace, "")

            send_config = create_config("http_resource", {
                "resource": "pol_harvester.wikipediacategorymembers",
                "wiki_country": language,
                "continuation_limit": 100
            })
            scc, err = send(category, config=send_config, method="get")
            print(f"Send {category_name}:", scc, err)
            resources = WikipediaCategoryMembers.objects.filter(id__in=scc)

            extract_config = {
                "objective": {
                    "@": "$.query.pages",
                    "pageid": "$.pageid",
                    "title": "$.title",
                    "categories": "$.categories",
                    "wikidata": "$.pageprops.wikibase_item",
                    "wikitext": "$.revisions.0.slots.main.*"
                }
            }
            prc = ExtractProcessor(config=extract_config)
            for resource in resources:
                results += prc.extract_from_resource(resource)

        corpus, created = Corpus.objects.get_or_create(name=corpus_name, identifier="pageid", schema={})
        articles = []
        for result in results:
            if not result["wikitext"]:
                continue
            result["text"] = self.clean_text(
                mwparserfromhell.parse(result["wikitext"]).strip_code(),
                category_namespace
            )
            articles.append(Article(properties=result, collection=corpus, schema={}))
        corpus.add(articles, reset=True)

        vectorizer = CountVectorizer()
        vectorizer.fit_transform([
            self.clean_text(doc.properties["text"], category_namespace)
            for doc in corpus.documents.all()
        ])
        dst = os.path.join(datagrowth_settings.DATAGROWTH_DATA_DIR, "custom_vocabulary", language)
        os.makedirs(dst, exist_ok=True)
        joblib.dump(vectorizer, os.path.join(dst, corpus_name + ".pkl"))
