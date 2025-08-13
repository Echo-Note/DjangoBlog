from django.apps import AppConfig


class DjangoblogAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "djangoblog"

    def ready(self):
        super().ready()
        # Import and load plugins here
        from .plugin_manage.loader import load_plugins

        load_plugins()

        # 确保在应用加载时导入admin，从而执行基于装饰器的注册
        # 仅导入以触发模块级注册逻辑，无需直接使用
        from . import logentryadmin  # noqa: F401
