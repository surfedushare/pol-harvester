from django.contrib import admin

from search.models import ElasticIndex, Query, QueryRanking


class ElasticIndexAdmin(admin.ModelAdmin):
    list_display = ("name", "remote_name", "remote_exists", "error_count", "language", "created_at", "modified_at",)


class QueryRankingAdminInline(admin.TabularInline):
    model = Query.users.through
    list_display = ("subquery", "freeze", "is_approved", "created_at", "modified_at")
    prepopulated_fields = {"slug": ("subquery",)}
    extra = 0


class QueryAdmin(admin.ModelAdmin):
    list_display = ("query", "created_at", "modified_at",)
    search_fields = ("query",)
    inlines = [QueryRankingAdminInline]


admin.site.register(ElasticIndex, ElasticIndexAdmin)
admin.site.register(Query, QueryAdmin)
