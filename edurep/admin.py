from django.contrib import admin

from datagrowth.admin import ResourceAdmin
from edurep.models import EdurepSearch, EdurepFile


admin.site.register(EdurepSearch, ResourceAdmin)
admin.site.register(EdurepFile, ResourceAdmin)
