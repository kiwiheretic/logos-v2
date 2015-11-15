# test plugin
from bot.pluginDespatch import Plugin
import re
import logging
from logos.settings import LOGGING
logger = logging.getLogger(__name__)
logging.config.dictConfig(LOGGING)

from bot.logos_decorators import irc_room_permission_required, \
    irc_network_permission_required

# decorator to ensure logos trigger function
# has ops in room and nick is in room
def check_ops(check_nick_in_room=False, use_current_room=False, me=False):
    def decorator(func):
        def func_wrapper(self, regex, chan, nick, **kwargs):
            if use_current_room:
                room = chan
            else:
                room = regex.group('room')   
                
            if me:
                this_nick = nick
            else:
                this_nick = regex.group('nick').lower()
                
            my_nick = self.get_nickname()
            
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
                return func(self, regex, chan, nick, **kwargs)
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
    plugin = ('room_manage', 'Room Management Plugin')
    
    def __init__(self, *args, **kwargs):
        # Change the line below to match the name of the class
        # you change this plugin to.
        super(RoomManagementPlugin, self).__init__(*args, **kwargs)
        self.commands = ((r'nicks', self.nicks, 'show nicks in room'),
                         (r'kick (?P<room>#\S+) (?P<nick>\S+)', self.kick_nick, 'kick nick from room'),
                         (r'ban (?P<room>#\S+) (?P<nick>\S+)', self.ban_nick, 'ban (mute) nick in room'),
                         (r'demo', self.demo, 'demonstrate say, describe and notice'),
                         (r'convo', self.convo, 'echo last lines of conversation'),
                         (r'timer', self.timer, 'demonstrates the timer in a plugin'),
                         (r'op me', self.op_me, 'gives ops'),
                         (r'deop me', self.deop_me, 'removes ops'),
                         (r'kick me', self.kick_me, 'kicks you off channel')
                         )
        self.conversation = []
    
    def privmsg(self, user, channel, message):
        # Append the last 10 messages into the conversation and delete
        # the other older ones
        self.conversation.append((user, channel, message))
        # keep only the last 10 items in the list
        self.conversation = self.conversation[-10:]

    def nicks(self, regex, chan, nick, **kwargs):

        nicks = self.get_room_nicks(chan)
        self.say(chan, "Nicks in room are " + ", ".join(nicks))

    def demo(self, regex, chan, nick, **kwargs):
     
        self.say(chan, "Elementary my dear Watson")
        self.describe(chan, "shakes its chains")
        self.notice(nick, "Now is the time for all good men...")

    
    def convo(self, regex, chan, nick, **kwargs):

        for u, c, m in self.conversation:
            self.say(chan, "%s said %s on %s" % (u,m,c))
    
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
    def op_me(self, regex, chan, nick, **kwargs):
        # using True is the same as +o
        self.mode(chan, True, "o", user = nick)

    @irc_room_permission_required('room_admin')
    @check_ops(use_current_room=True, me=True)    
    def deop_me(self, regex, chan, nick, **kwargs):
        # using False is the same as -o
        self.mode(chan, False, "o", user = nick)

    @irc_room_permission_required('room_admin')
    @check_ops(use_current_room=True, me=True)    
    def kick_me(self, regex, chan, nick, **kwargs):
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
        
    def joined(self, channel):
        self.say(channel, "I, Logos, have arrived")

    def userRenamed(self, old, new):
        self.notice(new, "You changed your nick from %s to %s" % (old, new))

    def userJoined(self, user, channel):
        self.say(channel, "%s has just joined %s" % (user,channel))

    def userLeft(self, user, channel):
        self.say(channel, "%s has just left %s" % (user,channel))

    def userQuit(self, user, quitMessage):
        # The control room or engine room is often the room designated for notices
        # and or messages if no other room is specified
        self.say(self.control_room, "%s has just quit with message  %s" % (user,quitMessage))
