import os
import logging
from tqdm import tqdm
from datetime import datetime
from urlobject import URLObject

from django.core.management.base import BaseCommand

from datagrowth.utils import ibatch, batchize
from pol_harvester.models import YouTubeDLResource


log = logging.getLogger("datascope")


class Command(BaseCommand):

    def handle(self, *args, **options):
        start = datetime(year=2018, month=11, day=15)
        end = datetime(year=2018, month=11, day=30)
        batch_size = 500
        queryset = YouTubeDLResource.objects.filter(
            created_at__gte=start,
            created_at__lt=end,
            uri__contains="youtube.com"
        )
        count = queryset.count()
        batch_iterator = ibatch(queryset.iterator(), batch_size=batch_size)
        if count >= batch_size * 5:
            batches, rest = batchize(count, batch_size)
            batch_iterator = tqdm(batch_iterator, total=batches)
        for instances in batch_iterator:
            for instance in instances:
                variables = instance.variables()
                url = URLObject(variables["url"])
                url = url.del_query_param('list')
                url = url.del_query_param('index')
                if variables["url"] ==  url:
                    continue
                instance.command["args"] = [url]
                instance.uri = instance.uri.replace(variables["url"], url)
                vid = url.query_dict["v"]
                content_type, files = instance.content
                for file in files:
                    if os.path.exists(file) and file.endswith(vid + ".wav" ):
                        instance.stdout = "[ffmpeg] Destination: {}".format(file)
                    elif os.path.exists(file):
                        os.remove(file)
                instance.save()
