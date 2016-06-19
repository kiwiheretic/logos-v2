# test plugin
from bot.pluginDespatch import Plugin
import re
import datetime
import dateutil
import logging
import httplib2

from django.conf import settings
from django.contrib.auth.models import User

from bot.logos_decorators import login_required

logger = logging.getLogger(__name__)
logging.config.dictConfig(settings.LOGGING)

class RedditPlugin(Plugin):
    plugin = ("reddit", "Reddit Plugin")
    def __init__(self, *args, **kwargs):
        Plugin.__init__(self, *args, **kwargs)

        self.commands = None
        self.userlist = {}

