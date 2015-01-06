# test plugin
from bot.pluginDespatch import Plugin
import re
import logging
from logos.settings import LOGGING
logger = logging.getLogger(__name__)
logging.config.dictConfig(LOGGING)

# If using this file as a starting point for your plugin
# then remember to change the class name 'MyBotPlugin' to
# something more meaningful.
class MyBotPlugin(Plugin):
    # Uncomment the line below to load this plugin
    #plugin = ('sample', 'My Bot Plugin')
    
    def __init__(self, *args, **kwargs):
        Plugin.__init__(self, *args, **kwargs)
        self.commands = ((r'nicks', self.nicks, 'show nicks in room'),
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

    def nicks(self, regex, **kwargs):
        chan = kwargs['channel']
        nicks = self.get_room_nicks(chan)
        self.say(chan, "Nicks in room are " + ", ".join(nicks))

    def demo(self, regex, **kwargs):
        nick = kwargs['nick']
        chan = kwargs['channel']        
        self.say(chan, "Elementary my dear Watson")
        self.describe(chan, "shakes its chains")
        self.notice(nick, "Now is the time for all good men...")

    
    def convo(self, regex, **kwargs):
        chan = kwargs['channel'] 
        for u, c, m in self.conversation:
            self.say(chan, "%s said %s on %s" % (u,m,c))
    
    def timer(self, regex, **kwargs):
        chan = kwargs['channel']         
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
      
    def op_me(self, regex, **kwargs):
        nick = kwargs['nick']
        chan = kwargs['channel']         
        # using True is the same as +o
        self.mode(chan, True, "o", user = nick)

    def deop_me(self, regex, **kwargs):
        nick = kwargs['nick']
        chan = kwargs['channel']         
        # using False is the same as -o
        self.mode(chan, False, "o", user = nick)

    def kick_me(self, regex, **kwargs):
        nick = kwargs['nick']
        chan = kwargs['channel']         
        self.kick(chan, nick, reason="Well, you asked ;)")
        
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
