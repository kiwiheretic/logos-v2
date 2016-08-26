from __future__ import absolute_import
from bot.pluginDespatch import Plugin
from bot.logos_decorators import irc_room_permission_required
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
         (r'praylist$', self.prayer_list, "List prayers"),
        )
    
    def privmsg(self, user, channel, message):
        logger.debug("note privmsg = " + str((user, channel, message)))
        simple_pms = get_room_option(self.network, room, "prayer-straightforward-pms")
        msg = message.strip()

        if simple_pms and channel[0] != "#":
            pvt_trigger = get_global_option('pvt-trigger')
            if not msg.startswith(pvt_trigger):
                logger.info("Prayer request: " + request)
                timestamp = datetime.datetime.utcnow()
                prayer = Prayer(timestamp=timestamp, nick=nick, 
                                   room=chan.lower(), 
                                   network = self.network,
                                   request=request) 
                prayer.save()
                self.say(chan, "Prayer request successfully recorded")
            
    @irc_room_permission_required('room_admin')
    def set_straightforward_pms(self, regex, chan, nick, **kwargs):
        """ Set the number of feed messages per feed limit """
        switched_on = regex.group('bool')
        if switched_on in ('off', 'on'):
            set_room_option(self.network, room, "prayer-straightforward-pms",
                    switched_on)
            self.say(chan,"Straightforwards pms set to "+switched_on)
        else:
            self.say(chan, "Mode should be \"on\" or \"off\"")

    def get_straightforward_pms(self, regex, chan, nick, **kwargs):
        """ Get the number of feed messages per feed """
        switched_on = get_room_option(self.network, room, "prayer-straightforward-pms")
        if switched_on == None: switched_on = "off"
        self.say(chan,"Straightforwards pms currently set to "+switched_on)

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
        prayers = Prayer.objects.filter(network=self.network,).order_by('-timestamp')
        for prayer in prayers[:10]:
            timestamp = prayer.timestamp.strftime("%-d %b, %H:%M")
            self.say(nick, "{} UTC {} -- {}".format(timestamp, prayer.nick, prayer.request))

