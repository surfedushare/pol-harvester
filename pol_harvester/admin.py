from django.contrib import admin

from datagrowth.resources import ResourceAdmin
from pol_harvester.models import KaldiAspireResource, HttpTikaResource


class KaldiAspireResourceAdmin(ResourceAdmin):
    pass


class HttpTikaResourceAdmin(ResourceAdmin):
    pass


admin.site.register(KaldiAspireResource, KaldiAspireResourceAdmin)
admin.site.register(HttpTikaResource, HttpTikaResourceAdmin)
