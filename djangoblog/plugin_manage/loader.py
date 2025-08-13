import os
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


def load_plugins():
    """
    从 “plugins” 目录动态加载和初始化插件。
    此函数旨在在Django应用程序注册表准备就绪时调用。
    """
    for plugin_name in settings.ACTIVE_PLUGINS:
        plugin_path = os.path.join(settings.PLUGINS_DIR, plugin_name)
        if os.path.isdir(plugin_path) and os.path.exists(
            os.path.join(plugin_path, "plugin.py")
        ):
            try:
                __import__(f"apps.plugins.{plugin_name}.plugin")
                logger.info(f"Successfully loaded plugin: {plugin_name}")
            except ImportError as e:
                logger.error(f"Failed to import plugin: {plugin_name}", exc_info=e)
