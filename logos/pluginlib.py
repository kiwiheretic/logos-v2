from __future__ import absolute_import
import inspect
from bot.pluginDespatch import Plugin
import logging
from django.conf import settings 
logger = logging.getLogger(__name__)
logging.config.dictConfig(settings.LOGGING)

class CommandDecodeException(Exception):
    def __init__(self, msg):
        self.msg = msg


def configure_app_plugins(app, plugins):
    """Populate plugins with configuration view information"""
    for plugin in plugins:
        # 'logos' app causes confusion because it
        # it matches the Plugin class
        try:
            plugin_mod = __import__(app + ".bot_plugin").bot_plugin
            for attr in dir(plugin_mod):
                a1 = getattr(plugin_mod, attr)
                # Check if the class is a class derived from 
                # bot.PluginDespatch.Plugin
                # but is not the base class only

                if inspect.isclass(a1) and \
                a1 != Plugin and \
                issubclass(a1, Plugin) and \
                hasattr(a1, 'plugin') and \
                a1.plugin[0] == plugin.name:  
                    if app == 'logos': 
                        plugin.user_view = 'logos.views.user_settings'
                        return

                    appmod = __import__(app + ".settings").settings
                    if hasattr(appmod, 'USER_SETTINGS_VIEW'):
                        plugin.user_view = appmod.USER_SETTINGS_VIEW
                        logger.debug( "Add user settings for " + app) 
                    if hasattr(appmod, 'SUPERUSER_SETTINGS_VIEW'):
                        plugin.superuser_view = appmod.SUPERUSER_SETTINGS_VIEW
                        logger.debug( "Add superuser settings for " + app) 
                    if hasattr(appmod, 'DASHBOARD_VIEW'):
                        plugin.dashboard_view = appmod.DASHBOARD_VIEW
                        logger.debug( "Add dashboard settings for " + app) 
                    if hasattr(appmod, 'BUTTON_NAME'):
                        plugin.button_name = appmod.BUTTON_NAME
                        logger.debug( "Add button name for " + app) 
                    return


        except ImportError:
            pass

