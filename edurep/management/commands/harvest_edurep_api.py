from django.core.management.base import BaseCommand

from datagrowth.resources.http.tasks import send


class Command(BaseCommand):

    def handle(self, *args, **options):
        config = {
            "resource": "edurep.EdurepSearch",
            "continuation_limit": 1000,
            "_namespace": "http_resource",
            "_private": ["_private", "_namespace", "_defaults"]
        }
        send("lom.educational.context=HO", config=config, method="get")
