"""自定义日志条目（LogEntry）在后台管理的展示与权限控制。

本模块使用自定义的 AdminSite 进行注册，并对以下方面进行了优化：
- 全字段只读，禁止新增/删除；
- 链接以 format_html 安全构建，避免 XSS 风险；
- 列表与搜索项优化，便于审计与追踪。
"""

from typing import Any, Dict, List, Optional
from django.contrib import admin
from django.contrib.admin.models import DELETION, LogEntry
from django.contrib.contenttypes.models import ContentType
from django.urls import NoReverseMatch, reverse
from django.utils.encoding import force_str
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.http import HttpRequest
from django.db.models.query import QuerySet

from djangoblog.admin_site import admin_site


@admin.register(LogEntry, site=admin_site)
class LogEntryAdmin(admin.ModelAdmin):
    """LogEntry 后台管理类。

    主要职责：
    - 定义列表页显示字段与过滤器；
    - 严格的权限限制（仅查看，不可新增/删除，且禁止 POST 修改）；
    - 以安全方式渲染对象和用户的跳转链接。
    """

    list_filter = ["content_type"]

    search_fields = ["object_repr", "change_message"]

    list_display_links = [
        "action_time",
        "get_change_message",
    ]
    list_display = [
        "action_time",
        "user_link",
        "content_type",
        "object_link",
        "get_change_message",
    ]

    def has_add_permission(self, request: HttpRequest) -> bool:
        """禁止新增日志条目。"""
        return False

    def has_change_permission(
        self, request: HttpRequest, obj: Optional[LogEntry] = None
    ) -> bool:
        """仅允许 GET 方式查看，禁止通过 POST 修改。

        超级用户或拥有 admin.change_logentry 权限的用户可以访问详情页，
        但 POST 操作会被拒绝，以确保日志不可被篡改。
        """
        return (
            request.user.is_superuser or request.user.has_perm("admin.change_logentry")
        ) and request.method != "POST"

    def has_delete_permission(
        self, request: HttpRequest, obj: Optional[LogEntry] = None
    ) -> bool:
        """禁止删除日志条目。"""
        return False

    def get_readonly_fields(
        self, request: HttpRequest, obj: Optional[LogEntry] = None
    ) -> List[str]:
        """将所有字段设为只读，确保后台只能查看，不能编辑。

        通过模型元信息动态获取字段名，避免遗漏；如需额外只读展示的方法字段，
        亦可在此方法返回值中追加。
        """
        return [f.name for f in LogEntry._meta.get_fields()]

    def object_link(self, obj: LogEntry) -> str:
        """返回对象的安全跳转链接（若可反解 URL）。

        若日志不是删除动作，尝试反向解析对象的修改页 URL，并以 format_html
        构建 HTML 超链接；若无法解析则回退为对象字符串。
        """
        content_type = ContentType.objects.get_for_id(obj.content_type_id)
        object_link = obj.object_repr
        if obj.action_flag != DELETION:
            # 尝试返回可点击的链接，提升审计便利性
            try:
                url = reverse(
                    "admin:{}_{}_change".format(
                        content_type.app_label, content_type.model
                    ),
                    args=[obj.object_id],
                )
                # 使用 format_html 安全构建链接，自动转义变量
                object_link = format_html('<a href="{}">{}</a>', url, object_link)
            except NoReverseMatch:
                # 无法反解 URL 时，直接返回字符串形式
                pass
        return object_link

    object_link.admin_order_field = "object_repr"
    object_link.short_description = _("object")

    def user_link(self, obj: LogEntry) -> str:
        """返回操作者的安全跳转链接（若可反解 URL）。"""
        content_type = ContentType.objects.get_for_model(type(obj.user))
        user_link = force_str(obj.user)
        try:
            # 尝试返回用户详情的可点击链接
            url = reverse(
                "admin:{}_{}_change".format(content_type.app_label, content_type.model),
                args=[obj.user.pk],
            )
            # 使用 format_html 安全构建链接
            user_link = format_html('<a href="{}">{}</a>', url, user_link)
        except NoReverseMatch:
            # 无法反解 URL 时，直接返回字符串形式
            pass
        return user_link

    user_link.admin_order_field = "user"
    user_link.short_description = _("user")

    def get_queryset(self, request: HttpRequest) -> "QuerySet[LogEntry]":
        """优化查询集，预取 content_type 以减少数据库查询次数。"""
        queryset = super(LogEntryAdmin, self).get_queryset(request)
        return queryset.prefetch_related("content_type")

    def get_actions(self, request: HttpRequest) -> Dict[str, Any]:
        """移除批量删除动作，避免通过批量操作删除日志。"""
        actions = super(LogEntryAdmin, self).get_actions(request)
        if "delete_selected" in actions:
            del actions["delete_selected"]
        return actions
