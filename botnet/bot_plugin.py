# test plugin
from __future__ import absolute_import
from bot.pluginDespatch import Plugin

from django.conf import settings
from django.contrib.auth.models import User

from bot.logos_decorators import login_required
from .models import BotNetGroups
import logging

logger = logging.getLogger(__name__)
logging.config.dictConfig(settings.LOGGING)

class BotNetPlugin(Plugin):
    plugin = ("botnet", "BotNet Plugin")
    def __init__(self, *args, **kwargs):
        Plugin.__init__(self, *args, **kwargs)

        self.relay_groups_init()
        self.commands = None
#        self.commands = (\
#         (r'activate', self.activate, "Activate BotNet"),
#        )


    def relay_groups_init(self):
        self.relay_groups=[]
        for group in BotNetGroups.objects.all():
            relay_group = {'channels':[], 'factories':[]}
            for room in group.botnetrooms_set.all():
                network = room.network
                room = room.room
                relay_group['channels'].append((network, room))
                for f in self.factory.factories:
                    if f.network == network:
                        if f not in relay_group['factories']:
                            relay_group['factories'].append(f)
            self.relay_groups.append(relay_group)


    def nicklist(self, channel):
        # Just choose first matching group at this point
        for group in self.relay_groups:
            if (self.network, channel.lower()) in group['channels']:
                userlist = []
                for f in group['factories']:
                    for network, chan in group['channels']:
                        # Skip the network and channel the nick is already on
                        # (They already have the irc nick list for their own
                        # network)
                        if self.network == network and chan == channel.lower():
                            continue
                        if network == f.network:
                            nicks = f.conn.nicks_db.get_room_nicks(channel)
                            for nick1 in nicks:
                                yield (f.network, chan, nick1)
                break  # Just do for first matching group


    def privmsg(self, user, channel, message):
        nick,_ = user.split('!')
        username = self.get_auth().get_username(nick)
        for group in self.relay_groups:
            if (self.network, channel.lower()) in group['channels']:
                for f in group['factories']:
                    for net, ch in group['channels']:
                        if f.network == net and (net != self.network or ch != channel.lower()):
                            msg = "{}/{}/{} ** {}".format(self.network, channel, nick, message)
                            f.conn.say(str(ch), msg)
                    

            pass


    def userJoined(self, nick, channel):
        """ Notify nick of who is in room when they join room """
        for network, chan, nnick in self.nicklist(channel):
            print (network, chan, nnick)
            msg = "{}/{}/{}".format(network, chan, nnick)
            self.notice(nick, msg)


    def userLeft(self, nick, channel):
        pass
