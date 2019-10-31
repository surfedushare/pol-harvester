from psycopg2 import OperationalError

from datagrowth.resources import KaldiNLResource as KaldiNL, KaldiAspireResource as KaldiEN


class KaldiNLResource(KaldiNL):

    def save(self, *args, **kwargs):
        try:
            super().save(*args, **kwargs)
        except OperationalError:
            print("Problem with KaldiNL command:", self.uri)
            self.stdout = ""
            super().save(*args, **kwargs)


class KaldiAspireResource(KaldiEN):

    def save(self, *args, **kwargs):
        try:
            super().save(*args, **kwargs)
        except OperationalError:
            print("Problem with KaldiAspire command:", self.uri)
            self.stdout = ""
            super().save(*args, **kwargs)
