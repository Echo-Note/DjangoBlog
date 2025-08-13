from django.contrib.admin import AdminSite


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
