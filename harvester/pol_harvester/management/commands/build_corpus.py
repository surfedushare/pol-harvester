import mwparserfromhell

from django.core.management.base import BaseCommand

from datagrowth.configuration import create_config
from datagrowth.resources.http.tasks import send
from datagrowth.processors.input.extraction import ExtractProcessor

from pol_harvester.models import Corpus, Article
from pol_harvester.models.wikipedia.categories import WikipediaCategoryMembers


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-c', '--category', type=str)
        parser.add_argument('-l', '--language', type=str)

    def handle(self, *args, **options):

        category = options["category"]
        language = options["language"]
        send_config = create_config("http_resource", {
            "resource": "pol_harvester.wikipediacategorymembers",
            "wiki_country": language,
            "continuation_limit": 100
        })
        scc, err = send(category, config=send_config, method="get")
        print("Send:", scc, err)
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
        results = []
        for resource in resources:
            results += prc.extract_from_resource(resource)

        corpus, created = Corpus.objects.get_or_create(name=category, identifier="pageid", schema={})
        articles = []
        for result in results:
            if not result["wikitext"]:
                continue
            result["text"] = mwparserfromhell.parse(result["wikitext"]).strip_code()
            articles.append(Article(properties=result, collection=corpus, schema={}))
        corpus.add(articles)

        for doc in corpus.documents.all():
            print(doc.properties["text"])
            print()
            print()
