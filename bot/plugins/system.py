# test plugin
import re
import pdb

import django
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

import twisted
import sys
import types
from logos.constants import VERSION

from bot.pluginDespatch import Plugin
from logos.roomlib import get_room_option, set_room_option, set_room_defaults,\
    set_global_option
    

from logos.pluginlib import Registry

import logging
from logos.settings import LOGGING
from logos.models import Settings

logger = logging.getLogger(__name__)
logging.config.dictConfig(LOGGING)


                
class SystemCoreCommands(Plugin):
    plugin = ("system", "System Module")
    

    
    def __init__(self, *args):
        super(SystemCoreCommands, self).__init__(*args)
        self.commands = ( \
                         (r'login\s+(?P<password>\w+)', self.login, 'Login into the bot'),
#                         (r'logout', self.logout, "Log out of bot"),
                         (r'version\s*$', self.version, "Show this bot's version info"),
                         (r'cmd\s+(.*)', self.cmd, "Have bot perform an IRC command"),
                         (r'say\s+(?P<room>#[a-zA-z0-9-]+)\s+(.*)', self.speak, "Say something into a room"),
                         (r'set\s+(?P<room>#[a-zA-z0-9-]+)\s+(?:activation|trigger)\s+\"(.)\"', self.set_trigger,
                           "Set the trigger used by the bot"),
                         (r'set\s+(?P<room>#[a-zA-z0-9-]+)\s+greet\s+message\s+\"(.*)\"', self.set_greet, 
                           "Set the autogreet message"),
                         (r'set\s+password\s+([^\s]+)', self.set_password, "Set your password"),
        )
        
        
        Registry.sys_authorized = []   # List of system authorized nicks - ie owner
        Registry.authorized = {}  
    
    
    def privmsg(self, user, channel, message):
        pass

#    def help(self, regex, chan, nick, **kwargs):
#        pass
    
    def login(self, regex, chan, nick, **kwargs):
        password = regex.group('password')
        host = self.get_host(nick)
        
        try:
            user = User.objects.get(username = nick.lower())
        except User.DoesNotExist:
            self.say(chan, "Invalid Nick")
            return
        
        if authenticate(username= nick.lower(), password= password):
            self.get_authenticated_users().add(nick, host, user)
            self.say(chan, "Login successful")
        else:
            self.say(chan, "Login failed")

#    def set_errors(self, regex, chan, nick, **kwargs):

#        if Registry.authorized.has_key(nick):
#            error_status = regex.group(1).strip().lower()
#            if error_status in ( "on", "off" ):
#                ch = Registry.authorized[nick]['channel']
#                set_room_option(self.factory.network, ch, \
#                    'error_status', error_status)
#                self.msg(chan, "Error status for %s set to %s " % (ch,error_status))
#            else:
#                self.msg(chan, "Unknown status \"%s\", expected 'on' or 'off' " % (errors_status,))            
            
    def speak(self, regex, chan, nick, **kwargs):

        ch = regex.group('room')
        if self.get_authenticated_users().is_authorised(nick, self.network, ch, 'speak'):

            text = regex.group(2)
            self.msg(ch, text)

    def set_greet(self, regex, chan, nick, **kwargs):
        ch = regex.group('room')
        if self.get_authenticated_users().is_authorised(nick, self.network, ch, 'set_greeting'):
            greet_msg = regex.group(2)
            set_room_option(self.factory.network, ch, \
                    'greet_message', greet_msg)
            self.msg(chan, "Greet message for %s set to \"%s\" " % (ch,greet_msg))  
                  
    def set_trigger(self, regex, chan, nick, **kwargs):
        ch = regex.group('room')
        if self.get_authenticated_users().is_authorised(nick, self.network, ch, 
                                                  'change_trigger'):
            # Command issued to bot to change the default activation
            # character.
            arg = regex.group(2)
            ch = regex.group('room')
            set_room_option(self.factory.network, ch, \
                'activation', arg)  

            self.msg(chan, "Trigger for room %s set to \"%s\"" % (ch,  arg))
            # Don't send this message twice if chan,ch are same room
            if chan != ch:
                self.msg(ch, "Trigger has been changed to \"%s\"" % (arg,)) 
        else:
            self.notice(nick, "You are not authorised to change trigger for this room")
                                      
    def cmd(self, regex, chan, nick, **kwargs):

        if self.get_authenticated_users().is_authorised(nick, self.network, chan, 'any_cmd'):
            # Have the bot issue any IRC command
            
            line = regex.group(1)
            logger.info("%s issued command '%s' to bot" % (nick, line))
            self.sendLine(line)
            
    def version(self, regex, chan, nick, **kwargs):

        dj_ver = ".".join(map(lambda x: str(x), django.VERSION[0:3]))
        pyver = (sys.version_info.major, sys.version_info.minor)
        py_ver = ".".join(map(lambda x: str(x), pyver))
        twstver = (twisted.version.major, twisted.version.minor)
        twst_ver = ".".join(map(lambda x: str(x), twstver))
        self.msg(chan, "\x033Logos Super Bot -- Version %s \x03" % (VERSION,))
        self.msg(chan, "\x0310--- Courtesy of\x03\x0312 SplatsCreations\x03")        
        self.msg(chan, "\x0310--- Built with Django %s\\Python %s\\Twisted %s  \x03" % (dj_ver, py_ver, twst_ver))        

        self.msg(chan, "\x1f\x0312https://github.com/kiwiheretic/logos-v2/")        
        
    def set_password(self, regex, chan, nick, **kwargs):

        if self.get_authenticated_users().is_authenticated(nick):
            pw = regex.group(1)
            self.get_authenticated_users().set_password(nick, pw)
            self.msg(chan, "Password set to %s " % (pw,))
                                 
    def joined(self, channel):
        # Add basic options to room setup
        defaults = ( ('activation', '!'),
                ( 'active', 1 ) )        
        set_room_defaults(self.factory.network, channel, defaults)
        set_room_option(self.factory.network, channel, 'active', 1)

    def left(self, channel):
        set_room_option(self.factory.network, channel, 'active', 0)
    
    def userJoined(self, nick, channel):
        greet_msg = get_room_option(self.factory.network, channel, 'greet_message')
        if greet_msg:
            greet_msg = re.sub("%nick%", nick, greet_msg)
            self.notice(nick, str(greet_msg))
            logger.info("Greet message sent to " + nick)
        
    def userRenamed(self, oldname, newname):
        self.get_authenticated_users().rename(oldname, newname)
        logger.info("renamed: {}".format(str(self.get_authenticated_users().users)))