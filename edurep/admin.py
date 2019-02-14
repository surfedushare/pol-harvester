from django.contrib import admin

from datagrowth.admin import HttpResourceAdmin
from edurep.models import EdurepSearch, EdurepFile


admin.site.register(EdurepSearch, HttpResourceAdmin)
admin.site.register(EdurepFile, HttpResourceAdmin)
