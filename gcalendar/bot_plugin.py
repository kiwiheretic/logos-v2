# test plugin
from bot.pluginDespatch import Plugin
import re
import datetime
import logging

from django.conf import settings
logger = logging.getLogger(__name__)
logging.config.dictConfig(settings.LOGGING)

class GoogleCalendarPlugin(Plugin):
    plugin = ("gcal", "Google Calendar Plugin")
    def __init__(self, *args, **kwargs):
        Plugin.__init__(self, *args, **kwargs)

        self.commands = ()
#        self.commands = (\
#         (r'urls\s+(?P<room>#[a-zA-z0-9-]+)\s+(?P<count>\d+)', self.urls_display, "display a list of captured urls"),
#         (r'urls\s+(?P<room>#[a-zA-z0-9-]+)$', self.urls_display, "display a list of captured urls"),
#        )
#    
