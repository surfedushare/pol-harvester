from django.contrib import admin

from datagrowth.admin import ResourceAdmin
from edurep.models import EdurepSearch

admin.site.register(EdurepSearch, ResourceAdmin)
