from django.contrib import admin

from ims.models import CommonCartridge


class CommonCartridgeAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'upload_at', 'metadata_tag')


class LTIAppAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'description', 'privacy_level', 'created_at', 'modified_at')


class LTICredentialsAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'organization', 'app', 'client_secret', 'created_at', 'modified_at')


admin.site.register(CommonCartridge, CommonCartridgeAdmin)
