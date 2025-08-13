from django.contrib.admin import AdminSite
from django.contrib.admin.models import LogEntry
from django.contrib.sites.admin import SiteAdmin
from django.contrib.sites.models import Site

from apps.accounts.admin import BlogUserAdmin
from apps.accounts.models import BlogUser
from apps.blog.admin import (
    ArticleAdmin,
    BlogSettingsAdmin,
    CategoryAdmin,
    LinksAdmin,
    SideBarAdmin,
    TagAdmin,
)
from apps.blog.models import Article, BlogSettings, Category, Links, SideBar, Tag
from apps.comments.admin import CommentAdmin
from apps.comments.models import Comment
from apps.oauth.admin import OAuthConfigAdmin, OAuthUserAdmin
from apps.oauth.models import OAuthConfig, OAuthUser
from apps.owntracks.admin import OwnTrackLogsAdmin
from apps.owntracks.models import OwnTrackLog
from apps.servermanager.admin import CommandsAdmin, EmailSendLogAdmin
from apps.servermanager.models import EmailSendLog, commands
from djangoblog.logentryadmin import LogEntryAdmin


class DjangoBlogAdminSite(AdminSite):
    site_header = "djangoblog administration"
    site_title = "djangoblog site admin"

    def __init__(self, name="admin"):
        super().__init__(name)

    def has_permission(self, request):
        return request.user.is_superuser

    # def get_urls(self):
    #     urls = super().get_urls()
    #     from django.urls import path
    #     from blog.views import refresh_memcache
    #
    #     my_urls = [
    #         path('refresh/', self.admin_view(refresh_memcache), name="refresh"),
    #     ]
    #     return urls + my_urls


admin_site = DjangoBlogAdminSite(name="admin")

admin_site.register(Article, ArticleAdmin)
admin_site.register(Category, CategoryAdmin)
admin_site.register(Tag, TagAdmin)
admin_site.register(Links, LinksAdmin)
admin_site.register(SideBar, SideBarAdmin)
admin_site.register(BlogSettings, BlogSettingsAdmin)

admin_site.register(commands, CommandsAdmin)
admin_site.register(EmailSendLog, EmailSendLogAdmin)

admin_site.register(BlogUser, BlogUserAdmin)

admin_site.register(Comment, CommentAdmin)

admin_site.register(OAuthUser, OAuthUserAdmin)
admin_site.register(OAuthConfig, OAuthConfigAdmin)

admin_site.register(OwnTrackLog, OwnTrackLogsAdmin)

admin_site.register(Site, SiteAdmin)

admin_site.register(LogEntry, LogEntryAdmin)
