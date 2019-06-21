from django.contrib import admin

from search.models import ElasticIndex


class ElasticIndexAdmin(admin.ModelAdmin):
    list_display = ("name", "remote_name", "remote_exists", "error_count", "language", "created_at", "modified_at",)


admin.site.register(ElasticIndex, ElasticIndexAdmin)
