from django.contrib import admin

from datagrowth.resources import ResourceAdmin
from pol_harvester.models import KaldiAspireResource, KaldiNLResource, HttpTikaResource


class KaldiAspireResourceAdmin(ResourceAdmin):
    pass


class KaldiNLResourceAdmin(ResourceAdmin):
    pass


class HttpTikaResourceAdmin(ResourceAdmin):
    pass


admin.site.register(KaldiAspireResource, KaldiAspireResourceAdmin)
admin.site.register(KaldiNLResource, KaldiNLResourceAdmin)
admin.site.register(HttpTikaResource, HttpTikaResourceAdmin)
