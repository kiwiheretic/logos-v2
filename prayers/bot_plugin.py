from __future__ import absolute_import
from bot.pluginDespatch import Plugin
import re
import datetime
import logging

from .models import Prayer
from django.conf import settings
logger = logging.getLogger(__name__)
logging.config.dictConfig(settings.LOGGING)

class PrayerPlugin(Plugin):
    plugin = ("prayer", "Prayer Requests Module")
    def __init__(self, *args, **kwargs):
        super(PrayerPlugin, self).__init__(*args, **kwargs)
        
        self.commands = (\
         (r'pray (?P<request>.*)$', self.new_prayer, "Add new prayer request to list"),
         (r'list$', self.prayer_list, "List prayers"),
        )
    
    def new_prayer(self, regex, chan, nick, **kwargs):
        request = regex.group('request').strip()
        if request:
            logger.info("Prayer request: " + request)
            timestamp = datetime.datetime.utcnow()
            prayer = Prayer(timestamp=timestamp, nick=nick, 
                               room=chan.lower(), 
                               network = self.network,
                               request=request) 
            prayer.save()
            self.say(chan, "Prayer request successfully recorded")
        else:
            self.say(chan, "You did not specify a prayer request")

    def prayer_list(self, regex, chan, nick, **kwargs):
        prayers = Prayer.objects.filter(network=self.network,
                room=chan.lower()).order_by('-timestamp')
        total = len(prayers)

        for prayer in prayers[:5]:
            timestamp = prayer.timestamp.strftime("%-d %b, %H:%M")
            self.say(nick, "{} {} -- {}".format(timestamp, prayer.nick, prayer.request))

