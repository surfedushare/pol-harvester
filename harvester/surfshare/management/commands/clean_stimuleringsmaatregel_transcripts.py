import os
import logging
from tqdm import tqdm

from django.core.management.base import BaseCommand

from datagrowth.utils import ibatch, batchize
from pol_harvester.models import KaldiNLResource


log = logging.getLogger("datascope")


class Command(BaseCommand):

    def handle(self, *args, **options):

        batch_size = 500
        queryset = KaldiNLResource.objects.all()
        count = queryset.count()
        batch_iterator = ibatch(queryset.iterator(), batch_size=batch_size)
        if count >= batch_size * 5:
            batches, rest = batchize(count, batch_size)
            batch_iterator = tqdm(batch_iterator, total=batches)

        for instances in batch_iterator:
            for instance in instances:
                variables = instance.variables()
                file = variables["input"][0]
                if not os.path.exists(file):
                    instance.delete()
