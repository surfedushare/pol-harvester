from django.contrib import admin

from datagrowth.resources import ResourceAdmin
from pol_harvester.models import KaldiAspireResource, KaldiNLResource, YouTubeDLResource, HttpTikaResource


class KaldiAspireResourceAdmin(ResourceAdmin):
    pass


class KaldiNLResourceAdmin(ResourceAdmin):
    pass


class YouTubeDLResourceAdmin(ResourceAdmin):
    pass


class HttpTikaResourceAdmin(ResourceAdmin):
    pass


admin.site.register(KaldiAspireResource, KaldiAspireResourceAdmin)
admin.site.register(KaldiNLResource, KaldiNLResourceAdmin)
admin.site.register(YouTubeDLResource, YouTubeDLResourceAdmin)
admin.site.register(HttpTikaResource, HttpTikaResourceAdmin)
