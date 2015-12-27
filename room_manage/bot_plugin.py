from __future__ import absolute_import
from bot.pluginDespatch import Plugin
import re
import logging
import pytz
import time
from twisted.internet.task import LoopingCall
from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings
from .models import DownVotes, Penalty, Probation, NickHistory

logger = logging.getLogger(__name__)
logging.config.dictConfig(settings.LOGGING)

DOWN_VOTE_MINUTES = 5
DOWN_VOTES_REQUIRED = 1
PENALTY_TIME = 120

MIN_FLOOD_INTERVAL = 5  # In Seconds
FLOOD_THRESHHOLD = 3
FLOOD_PENALTY_TIME = 60*5 # Flood penalty in seconds

from bot.logos_decorators import irc_room_permission_required, \
    irc_network_permission_required

# decorator to ensure logos trigger function
# has ops in room and nick is in room
def check_ops(check_nick_in_room=False, use_current_room=False, me=False):
    def decorator(func):
        def func_wrapper(self, regex, chan, nick, **kwargs):
            if use_current_room:
                if chan[0] == "#":
                    room = chan
                else: # If in a private message window
                    room = None
            else:
                try:
                    room = regex.group('room')   
                except IndexError:
                    room = None
                    
            if me:
                this_nick = nick
            else:
                this_nick = regex.group('nick').lower()
                
            my_nick = self.get_nickname()
            
            if room: # not private message or no current room
                if room.lower() not in self.get_rooms():
                    self.notice(nick, 'I am not in room {}'.format(room))
                    return
                    
                my_ops = self.get_op_status(my_nick, room)
                if my_ops is None or my_ops not in "~@&":
                    self.notice(nick, 'I do not have ops in room {}'.format(room))
                    return
                    
                if check_nick_in_room and this_nick not in self.get_room_nicks(room):
                    self.notice(nick, 'user {} is not in room'.format(this_nick))
                else:
                    return func(self, regex, [chan], nick, **kwargs)
            else: # is private message
                rooms = self.get_rooms_for_nick(nick)
                opped_rooms = []
                for room in rooms:
                    # make sure the room management plugin is enabled
                    # in all rooms we are acting in
                    if self.is_plugin_enabled(room):
                        my_ops = self.get_op_status(my_nick, room)
                        if my_ops and my_ops in "~@&": # make sure I have ops
                            # Make sure nick is in room action is requested
                            if nick in self.get_room_nicks(room):
                                opped_rooms.append(room)
                if not opped_rooms:
                    self.notice(nick, 'I do not have ops in any enabled rooms you are in')
                    return
                return func(self, regex, opped_rooms, nick, **kwargs)
        
        return func_wrapper
    return decorator

# To test this plugin remember to type the following
# commands on IRC where the bot can see them:
# !activste plugin room_manage
# !enable plugin #myroom room_manage
# Change #myroom to be whatever room you are in.

class RoomManagementPlugin(Plugin):
    # Uncomment the line below to load this plugin.  Also if
    # you are using this as a starting point for your own plugin
    # remember to change 'sample' to be a unique identifier for your plugin,
    # and 'My Bot Plugin' to a short description for your plugin.
    plugin = ('rm', 'Room Management Plugin')
    
    def __init__(self, *args, **kwargs):
        # Change the line below to match the name of the class
        # you change this plugin to.
        super(RoomManagementPlugin, self).__init__(*args, **kwargs)
        self.repeater = LoopingCall(self.repeat)
        self.repeater.start(30, now = True)
        
        self.commands = ((r'nicks', self.nicks, 'show nicks in room'),
                         (r'kick (?P<room>#\S+) (?P<nick>\S+)', self.kick_nick, 'kick nick from room'),
                         (r'ban (?P<room>#\S+) (?P<nick>\S+)', self.ban_nick, 'ban (mute) nick in room'),
                         (r'remove penalty (?P<room>#\S+) (?P<nick>\S+)', self.remove_penalty, 'remove room penalty'),
                         # (r'down vote (?P<nick>\S+)', self.down_vote, 'Down vote a nick'),
                         # (r'dv (?P<nick>\S+)', self.down_vote, 'Down vote a nick'),
                         
                         (r'timer', self.timer, 'demonstrates the timer in a plugin'),
                         # (r'mute (?P<room>#\S+) (?P<nick>\S+)', self.mute, 'normal user despatch'),
                         # (r'mute (?P<nick>\S+)', self.mute, 'normal user despatch'),
                         (r'op me', self.op_me, 'gives ops'),
                         (r'deop me', self.deop_me, 'removes ops'),
                         (r'kick me', self.kick_me, 'kicks you off channel')
                         )
        self.antiflood = {}
    
    def get_hostmask(self, nick):
        hostmask = self.get_host(nick).split('@')[1]
        if hostmask:
            host_mask = '*!*@'+hostmask
        else:
            host_mask = nick+'!*@*'
        return host_mask
        
    def repeat(self):
        for penalty in Penalty.objects.filter(network = self.network):
            if timezone.now() > penalty.end_time:
                self.mode( penalty.room, False, "b", mask = penalty.nick_mask)
                penalty.delete()

    
    def privmsg(self, user, channel, message):
        # Anti-flood checks
        if self.is_plugin_enabled(channel):
            my_nick = self.get_nickname()
            
            my_ops = self.get_op_status(my_nick, channel)
            if my_ops is not None and my_ops in "~@&%":
                nick, user_mask = user.split('!')
                nick = nick.lower()
                user_mask = '*!'+user_mask
                logger.debug("{} has user_mask {}".format(nick, user_mask))
                timestamp = time.time()
                if nick in self.antiflood:
                    if channel in self.antiflood[nick]:
                        if message == self.antiflood[nick][channel]['line']:
                            prior_time = self.antiflood[nick][channel]['timestamp']
                            if timestamp - prior_time < MIN_FLOOD_INTERVAL:
                                self.antiflood[nick][channel]['repeat'] += 1
                                self.antiflood[nick][channel]['timestamp'] = timestamp
                                if self.antiflood[nick][channel]['repeat'] >= FLOOD_THRESHHOLD:
                                    self.add_penalty(channel, user_mask, FLOOD_PENALTY_TIME, reason="flooding")
                                    self.kick(channel, nick, reason = "Stop repeating yourself!")                                    
                            else:
                                self.antiflood[nick][channel] = {'line':message, 'timestamp':timestamp, 'repeat':0}
                        else:
                            self.antiflood[nick][channel] = {'line':message, 'timestamp':timestamp, 'repeat':0}
                    else:
                        self.antiflood[nick][channel] = {'line':message, 'timestamp':timestamp, 'repeat':0}
                else:
                    self.antiflood[nick] = { channel: {'line':message, 'timestamp':timestamp, 'repeat':0} }
                print self.antiflood
                    

    def add_penalty(self, channel, user_mask, seconds, reason=None):
        begin_date = timezone.now()
        end_date = begin_date + timedelta(seconds = seconds)
        wmask = '*!*@'+user_mask.split('@')[1]
        penalty = Penalty(network = self.network.lower(),
            room = channel.lower(),
            nick_mask = wmask,
            reason = reason,
            begin_time = begin_date,
            end_time = end_date,
            kick = True)
        penalty.save()

    @irc_room_permission_required('room_admin')
    def remove_penalty(self, regex, chan, nick, **kwargs):
        this_nick = regex.group('nick')
        this_room = regex.group('room')
        hostmask = self.get_hostmask(this_nick)
        wmask = '*!*@' + hostmask.split('@')[1]
        penalties = Penalty.objects.filter(nick_mask = wmask,
                               room = this_room.lower(),
                               end_time__gt = timezone.now())
        for penalty in penalties:
            penalty.kick = False
            penalty.save()
        self.notice(nick, "Penalty removed")
    
    @check_ops()
    def down_vote(self, regex, chans, nick, **kwargs):
        nick_dv = regex.group('nick')
        hostmask = self.get_hostmask(nick_dv)
        if not hostmask:
            self.notice(nick, "No hostmask available yet")
            return
        
        for chan in chans:
            dvs = DownVotes.objects.filter(network=self.network.lower(),
                room = chan.lower(),
                nick_mask = hostmask,
                downvoting_nick = nick.lower(),
                downvote_datetime__gte = timezone.now() - timedelta(seconds = 60*DOWN_VOTE_MINUTES))
            if dvs.exists():
                self.notice(chan, "You down voted {} within {} minutes ago".format(nick_dv, DOWN_VOTE_MINUTES))
            else:
                dv = DownVotes(network = self.network.lower(),
                                room = chan.lower(),
                                nick_mask = hostmask,
                                downvoting_nick = nick.lower())
                dv.save()
                self.notice(nick, "Nick {} in channel {} down voted".format(nick_dv, chan))
            
            dvs_count = DownVotes.objects.filter(network=self.network.lower(),
                room = chan.lower(),
                nick_mask = hostmask,
                downvote_datetime__gte = timezone.now() - timedelta(seconds = 60*DOWN_VOTE_MINUTES)).count()
            if dvs_count >= DOWN_VOTES_REQUIRED:
                begin_date = timezone.now()
                end_date = begin_date + timedelta(seconds = PENALTY_TIME)
                penalty = Penalty(network = self.network.lower(),
                    room = chan.lower(),
                    nick_mask = hostmask,
                    begin_time = begin_date,
                    end_time = end_date,
                    kick = True)
                penalty.save()
                self.kick(chan, nick_dv, reason = "down voted by democracy, not allowed in room for {} minutes".format(PENALTY_TIME/60))
                
            
        
    def nicks(self, regex, chan, nick, **kwargs):
        nicks = self.get_room_nicks(chan)
        nick_plus_hosts = []
        for nck in nicks:
            nick_plus_hosts.append(nck + " :) " + self.get_hostmask(nck) )
        self.notice(nick, "Nicks in room are " + ", ".join(nick_plus_hosts))

        
    def mute(self, regex, chan, nick, **kwargs):
        """Send a probationary nick away"""
        try:
            room = regex.group('room')
        except IndexError:
            room = chan
            
        this_nick = regex.group('nick')
        hostmask = self.get_hostmask(nick)
        if Probation.objects.filter(network = self.network, room = room, host_mask = hostmask).exists():
            pen, created = Penalty.objects.get_or_create(network = self.network, room = room, host_mask = banmask)
            if not created:
                pen.begin_time = timezone.now()
                pen.end_time = pen.begin_time + timedelta(seconds = 30)
                pen.save()
                self.mode( room, True, "b", mask = banmask)

        
    def timer(self, regex, chan, nick, **kwargs):
         
        self.reactor.callLater(5, self.timer_expired, chan)
        self.say(chan, "The timer will expire in 5 seconds")

    def timer_expired(self, chan):
        self.say(chan, "The timer has expired after 5 seconds")

#        self.mode( chan, set, modes, limit = None, user = None, mask = None):
#        Demonstration of changeing the modes on a user or channel.
        
#        Explanation of parameters below:
        
#        The {limit}, {user}, and {mask} parameters are mutually exclusive.

#        chan: The name of the channel to operate on.
#        set: True to give the user or channel permissions and False to
#            remove them.
#        modes: The mode flags to set on the user or channel.
#        limit: In conjuction with the {'l'} mode flag, limits the
#             number of users on the channel.
#        user: The user to change the mode on.
#        mask: In conjuction with the {'b'} mode flag, sets a mask of
#            users to be banned from the channel.  

    @irc_room_permission_required('room_admin')
    @check_ops(use_current_room=True, me=True)      
    def op_me(self, regex, chans, nick, **kwargs):
        # using True is the same as +o
        for chan in chans:
            if self.is_plugin_enabled(chan):
                self.mode(chan, True, "o", user = nick)

    @irc_room_permission_required('room_admin')
    @check_ops(use_current_room=True, me=True)    
    def deop_me(self, regex, chan, nick, **kwargs):
        # using False is the same as -o
        for chan in chans:
            if self.is_plugin_enabled(chan):
                self.mode(chan, False, "o", user = nick)

    @irc_room_permission_required('room_admin')
    @check_ops(use_current_room=True, me=True)    
    def kick_me(self, regex, chans, nick, **kwargs):
        for chan in chans:
            if self.is_plugin_enabled(chan):
                self.kick(chan, nick, reason="Well, you asked ;)")
        
    @irc_room_permission_required('room_admin')
    @check_ops(check_nick_in_room=True)
    def kick_nick(self, regex, chan, nick, **kwargs):
        room = regex.group('room')
        nick_to_kick = regex.group('nick')
        self.kick(room, nick, reason="No reason given.")
    
    @irc_room_permission_required('room_admin')
    @check_ops(check_nick_in_room=True)
    def ban_nick(self, regex, chan, nick, **kwargs):
        room = regex.group('room')
        nick_to_ban = regex.group('nick').lower()
        hostmask = self.get_host(nick_to_ban)
        if hostmask:
            wmask = "*!*@" + hostmask.split('@')[1]
            self.notice(nick, 'banning user {} with mask {}'.format(nick_to_ban, wmask))
        else:
            self.notice(nick, 'host mask for user {} unknown'.format(nick_to_ban))
        
    def border_patrol(self, args):
        action, nick, room = args
        hostmask = self.get_hostmask(nick)
        penalty = Penalty.objects.filter(network = self.network.lower(),
                room = room.lower(),
                nick_mask = hostmask,
                end_time__gt = timezone.now()).order_by('end_time').last()
        if penalty and penalty.kick:
            time_remaining = (penalty.end_time - timezone.now()).seconds
            hours = time_remaining/3600
            time_remaining -= hours*3600
            minutes = time_remaining/60
            seconds = time_remaining - minutes*60
            
            msg = "Not allowed in {} for {} hours {} minutes and {} seconds for {}".format(room, hours, minutes, seconds, penalty.reason)
            
            if action == "kick":
                self.kick(room, nick, reason = msg)
            elif action == "mute":
                self.mode( penalty.room, True, "b", mask = penalty.nick_mask)
        
    
    def joined(self, channel):
        pass

    def userRenamed(self, old, new):
        pass

    def userJoined(self, user, channel):
        pass

    def userLeft(self, user, channel):
        pass

    def userQuit(self, user, quitMessage):
        # The control room or engine room is often the room designated for notices
        # and or messages if no other room is specified
        self.say(self.control_room, "%s has just quit with message  %s" % (user,quitMessage))
        
    def userHosts(self, nicklist):
        """ Called when userhost info is available """
        # The _ throws away unneeded userhost
        for nick, userhost in nicklist:
            host = "*!*@" + userhost.split('@')[1]
            logger.debug( str((nick, host)) )
            rooms = self.get_rooms_for_nick(nick)
            for room in rooms:
                hist = NickHistory(network = self.network, room=room, nick = nick, host_mask = host)
                hist.save()
                self.border_patrol(('kick', nick, room))