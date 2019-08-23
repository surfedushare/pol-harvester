from django.contrib import admin

from datagrowth.admin import ShellResourceAdmin, HttpResourceAdmin, DataStorageAdmin, DocumentAdmin, AnnotationAdmin
from pol_harvester.models import (KaldiAspireResource, KaldiNLResource, YouTubeDLResource, HttpTikaResource,
                                  Freeze, Collection, Arrangement, Document, Annotation,
                                  WikipediaCategoryMembers, Corpus, Article)


class KaldiAspireResourceAdmin(ShellResourceAdmin):
    pass


class KaldiNLResourceAdmin(ShellResourceAdmin):
    pass


class YouTubeDLResourceAdmin(ShellResourceAdmin):
    pass


class HttpTikaResourceAdmin(HttpResourceAdmin):
    pass


class ExtendedDocumentAdmin(DocumentAdmin):
    list_display = ['__str__', 'freeze', 'collection', 'arrangement', 'created_at', 'modified_at']
    list_filter = ('freeze', 'collection',)


admin.site.register(KaldiAspireResource, KaldiAspireResourceAdmin)
admin.site.register(KaldiNLResource, KaldiNLResourceAdmin)
admin.site.register(YouTubeDLResource, YouTubeDLResourceAdmin)
admin.site.register(HttpTikaResource, HttpTikaResourceAdmin)

admin.site.register(Freeze, DataStorageAdmin)
admin.site.register(Collection, DataStorageAdmin)
admin.site.register(Arrangement, DataStorageAdmin)
admin.site.register(Document, ExtendedDocumentAdmin)
admin.site.register(Annotation, AnnotationAdmin)

admin.site.register(WikipediaCategoryMembers, HttpResourceAdmin)
admin.site.register(Corpus, DataStorageAdmin)
admin.site.register(Article, DataStorageAdmin)
