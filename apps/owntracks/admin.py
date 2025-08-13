from django.contrib import admin

from apps.owntracks.models import OwnTrackLog
from djangoblog.admin_site import admin_site


# Register your models here.
@admin.register(OwnTrackLog, site=admin_site)
class OwnTrackLogsAdmin(admin.ModelAdmin):
    pass
