from django.apps import AppConfig


class CommentsConfig(AppConfig):
    name = "apps.comments"

    def ready(self):
        # 确保在应用加载时导入admin，从而执行基于装饰器的注册
        # 仅导入以触发模块级注册逻辑，无需直接使用
        from . import admin  # noqa: F401
