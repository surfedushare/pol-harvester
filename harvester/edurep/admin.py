from django.contrib import admin

from datagrowth.admin import HttpResourceAdmin
from edurep.models import EdurepSearch, EdurepFile, EdurepSource, EdurepOAIPMH


class EdurepSourceAdmin(admin.ModelAdmin):
    list_display = ("name", "query", "created_at", "modified_at")


class EdurepHarvestAdminInline(admin.TabularInline):
    model = EdurepSource.freezes.through
    fields = ("source", "completed_at", "latest_update_at", "stage",)
    readonly_fields = ("completed_at",)
    extra = 0


admin.site.register(EdurepSearch, HttpResourceAdmin)
admin.site.register(EdurepFile, HttpResourceAdmin)
admin.site.register(EdurepSource, EdurepSourceAdmin)
admin.site.register(EdurepOAIPMH, HttpResourceAdmin)
