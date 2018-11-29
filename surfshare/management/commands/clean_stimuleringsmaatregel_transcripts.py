import os
import logging
from tqdm import tqdm
from datetime import datetime
from urlobject import URLObject

from django.core.management.base import BaseCommand

from datagrowth.utils import ibatch, batchize
from pol_harvester.models import YouTubeDLResource, KaldiNLResource


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

        keep = []
        delete = []
        for instances in batch_iterator:
            for instance in instances:
                variables = instance.variables()
                file = variables["input"]
                if not os.path.exists(file):
                    delete.append(instance.id)
                else:
                    keep.append(instance.id)
        print(len(keep), len(delete))
