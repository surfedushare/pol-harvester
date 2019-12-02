from datetime import datetime

from django.db import models
from django.db.utils import OperationalError

from datagrowth.resources import KaldiNLResource as KaldiNL, KaldiAspireResource as KaldiEN


class KaldiNLResource(KaldiNL):

    runtime = models.FloatField(null=True, blank=True)

    def _run(self):
        t0 = datetime.now()
        super()._run()
        t1 = datetime.now()
        runtime = t1 - t0
        self.runtime = float(runtime.seconds)

    def save(self, *args, **kwargs):
        # This is a tough cookie
        # Really not sure why at the first try the Postgres seems to be shutdown and with a second try it always works.
        # Tried some Postgres setting as well as reconnect packages all to no avail
        # For now we're simply retrying once and leave it at that
        try:
            super().save(*args, **kwargs)
        except OperationalError:
            super().save(*args, **kwargs)


class KaldiAspireResource(KaldiEN):

    runtime = models.FloatField(null=True, blank=True)

    def _run(self):
        t0 = datetime.now()
        super()._run()
        t1 = datetime.now()
        runtime = t1 - t0
        self.runtime = float(runtime.seconds)

    def save(self, *args, **kwargs):
        # This is a tough cookie
        # Really not sure why at the first try the Postgres seems to be shutdown and with a second try it always works.
        # Tried some Postgres setting as well as reconnect packages all to no avail
        # For now we're simply retrying once and leave it at that
        try:
            super().save(*args, **kwargs)
        except OperationalError:
            super().save(*args, **kwargs)
