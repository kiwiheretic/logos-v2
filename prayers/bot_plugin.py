from __future__ import absolute_import
from bot.pluginDespatch import Plugin
from bot.logos_decorators import irc_network_permission_required
from twisted.internet import task
import re
from datetime import datetime, timedelta
import logging

from .models import Prayer
from django.conf import settings
from django.utils import timezone

from logos.roomlib import get_room_option, set_room_option, get_global_option, set_global_option

logger = logging.getLogger(__name__)
logging.config.dictConfig(settings.LOGGING)

TIMER_SCHEDULE = 60*60

class PrayerPlugin(Plugin):
    plugin = ("prayer", "Prayer Requests Module")
    def __init__(self, *args, **kwargs):
        super(PrayerPlugin, self).__init__(*args, **kwargs)
        
        self.commands = (\
         (r'pray (?P<request>.*)$', self.new_prayer, "Add new prayer request to list"),
         (r'list$', self.prayer_list, "List prayers"),
         (r'praylist$', self.prayer_list, "List prayers"),
         (r'set straightforward pms (?P<bool>\w+)$', self.set_straightforward_pms, "Set whether private messages are assumed to be prayers"),
         (r'get straightforward pms$', self.get_straightforward_pms, "Get whether private messages are assumed to be prayers or not"),
         (r'set expiry days (\d+)$', self.set_expiry_days, "Set when to remove prayers from list"),
         (r'get expiry days$', self.get_expiry_days, "Show when prayers are removed from list"),
        )
        self.timer = task.LoopingCall(self.on_timer)
    
    def on_activate(self):
        """ When this plugin is activated for the network """
        self.timer.start(TIMER_SCHEDULE, now=False)
        logger.info("Prayer expiration timer started")
        return (True, None)

    def on_deactivate(self):
        """ When this plugin is deactivated for the network """
        self.timer.stop()
        logger.info("Prayer expiration timer stopped")

    def on_timer(self):
        logger.debug("Prayer timer invoked")
        try:
            expiry_days= int(get_global_option("prayer-expiry-days"))
        except TypeError: # if option not set
            expiry_days = 7

        Prayer.objects.filter(timestamp__lt = timezone.now() - timedelta(days=expiry_days)).delete()

    def privmsg(self, user, channel, message):
        logger.debug("note privmsg = " + str((user, channel, message)))
        simple_pms = get_room_option(self.network, channel, "prayer-straightforward-pms")
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
            
    @irc_network_permission_required('bot_admin')
    def set_straightforward_pms(self, regex, chan, nick, **kwargs):
        """ Set the number of feed messages per feed limit """
        switched_on = regex.group('bool')
        if switched_on in ('off', 'on'):
            set_room_option(self.network, chan, "prayer-straightforward-pms",
                    switched_on)
            self.say(chan,"Straightforwards pms set to "+switched_on)
        else:
            self.say(chan, "Mode should be \"on\" or \"off\"")

    def get_straightforward_pms(self, regex, chan, nick, **kwargs):
        """ Get the number of feed messages per feed """
        switched_on = get_room_option(self.network, chan, "prayer-straightforward-pms")
        if switched_on == None: switched_on = "off"
        self.say(chan,"Straightforwards pms currently set to "+switched_on)

    @irc_network_permission_required('bot_admin')
    def set_expiry_days(self, regex, chan, nick, **kwargs):
        """ Set the number of days to wait before expiring prayers"""
        days = regex.group(1)
        set_global_option("prayer-expiry-days", days)
        self.say(chan,"Expiry days set to "+days)

    def get_expiry_days(self, regex, chan, nick, **kwargs):
        """ Get the number of days to wait before expiring prayers"""
        days = get_global_option("prayer-expiry-days")
        self.say(chan,"Number of days before expiring prayers = "+days)

    def new_prayer(self, regex, chan, nick, **kwargs):
        request = regex.group('request').strip()
        if request:
            logger.info("Prayer request: " + request)
            timestamp = timezone.make_aware(datetime.utcnow())
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
        self.say(nick, "List of prayer requests")
        for prayer in prayers[:30]:
            timestamp = prayer.timestamp.strftime("%-d %b, %H:%M")
            self.say(nick, "{} UTC {} -- {}".format(timestamp, prayer.nick, prayer.request))
        self.say(nick, "----- end of prayer requests -----")

