from django.contrib import admin

from apps.servermanager.models import EmailSendLog, commands
from djangoblog.admin_site import admin_site


# Register your models here.


@admin.register(commands, site=admin_site)
class CommandsAdmin(admin.ModelAdmin):
    list_display = ("title", "command", "describe")


@admin.register(EmailSendLog, site=admin_site)
class EmailSendLogAdmin(admin.ModelAdmin):
    list_display = ("title", "emailto", "send_result", "creation_time")
    readonly_fields = ("title", "emailto", "send_result", "creation_time", "content")

    def has_add_permission(self, request):
        return False
