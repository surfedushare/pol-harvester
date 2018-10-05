from django.contrib import admin

from datagrowth.resources import ResourceAdmin
from pol_harvester.models import KaldiAspireResource


class KaldiAspireResourceAdmin(ResourceAdmin):
    pass


admin.site.register(KaldiAspireResource, KaldiAspireResourceAdmin)
