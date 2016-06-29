from __future__ import absolute_import
from django.conf import settings
from .models import Plugins
from .pluginlib import configure_app_plugins
from .roomlib import get_global_option

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

    ctx = {'menu_buttons':menu_buttons}

    # ----- Get site name and tag lines if exist
    site_name = get_global_option('site-name')
    tag_line = get_global_option('tag-line')
    ctx.update({'logos_site_name':site_name, 'tag_line': tag_line})
    return ctx
