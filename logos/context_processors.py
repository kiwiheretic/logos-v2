from __future__ import absolute_import
from django.conf import settings
from .models import Plugins
from .pluginlib import configure_app_plugins
import logging
from django.conf import settings 
logger = logging.getLogger(__name__)
logging.config.dictConfig(settings.LOGGING)

def request(ctx):
    plugins = Plugins.objects.order_by('name')
    for app in settings.INSTALLED_APPS:
        configure_app_plugins(app, plugins)
    menu_buttons = []
    for plugin in plugins:
        if hasattr(plugin, 'button_name') and hasattr(plugin, 'dashboard_view'):
            logger.debug("Menuing plugin "+plugin.name)
            dview = plugin.dashboard_view
            bname = plugin.button_name
            menu_buttons.append((bname, dview))

    return {'menu_buttons':menu_buttons}
