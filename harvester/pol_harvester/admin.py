from django.contrib import admin

from datagrowth.admin import ShellResourceAdmin, HttpResourceAdmin, DataStorageAdmin
from pol_harvester.models import (KaldiAspireResource, KaldiNLResource, YouTubeDLResource, HttpTikaResource, Freeze,
                                  Collection, Arrangement, Document)


class KaldiAspireResourceAdmin(ShellResourceAdmin):
    pass


class KaldiNLResourceAdmin(ShellResourceAdmin):
    pass


class YouTubeDLResourceAdmin(ShellResourceAdmin):
    pass


class HttpTikaResourceAdmin(HttpResourceAdmin):
    pass


admin.site.register(KaldiAspireResource, KaldiAspireResourceAdmin)
admin.site.register(KaldiNLResource, KaldiNLResourceAdmin)
admin.site.register(YouTubeDLResource, YouTubeDLResourceAdmin)
admin.site.register(HttpTikaResource, HttpTikaResourceAdmin)

admin.site.register(Freeze, DataStorageAdmin)
admin.site.register(Collection, DataStorageAdmin)
admin.site.register(Arrangement, DataStorageAdmin)
admin.site.register(Document, DataStorageAdmin)
