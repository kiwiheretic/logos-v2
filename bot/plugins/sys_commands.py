# test plugin
import re
import pdb

import django
import twisted
import sys
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

class SystemCommandsClass(Plugin):
    priority="system"
    
    def __init__(self, *args):
        super(SystemCommandsClass, self).__init__(*args)
        self.commands = ((r'auth\s+#(#?[a-zA-Z0-9_-]+)\s+(.+)',self.auth, \
                          "Authorise access to a room"),
                         (r'logout', self.logout, "Log out of bot"),
                         (r'sysauth\s(.+)', self.sysauth, "Perform a system login"),
                         (r'version\s*$', self.version, "Show this bot's version info"),
                         (r'cmd\s+(.*)', self.cmd, "Have bot perform an IRC command"),
                         (r'set\s+(?:activation|trigger)\s+\"(.)\"', self.set_trigger,
                           "Set the trigger used by the bot"),
                         (r'set\s+greet\s+message\s+\"(.*)\"', self.set_greet, 
                           "Set the autogreet message"),
                         (r'set\s+errors\s+(.*)', self.set_errors, 
                          "Set whether errors go to room or not"),
                         (r'set\s+password\s+\"([^"]+)\"', self.set_password, "Set your password"),
                         (r'syslogout', self.syslogout, "Perform a system logout"),
        )
        Registry.sys_authorized = []   # List of system authorized nicks - ie owner
        Registry.authorized = {}  
    
    def privmsg(self, user, channel, message):
        pass

    
    def set_errors(self, regex, **kwargs):
        nick = kwargs['nick'] 
        chan = kwargs['channel']
        if Registry.authorized.has_key(nick):
            error_status = regex.group(1).strip().lower()
            if error_status in ( "on", "off" ):
                ch = Registry.authorized[nick]['channel']
                set_room_option(self.factory.network, ch, \
                    'error_status', error_status)
                self.msg(chan, "Error status for %s set to %s " % (ch,error_status))
            else:
                self.msg(chan, "Unknown status \"%s\", expected 'on' or 'off' " % (errors_status,))            
            
    def set_greet(self, regex, **kwargs):
        nick = kwargs['nick'] 
        chan = kwargs['channel']
        if Registry.authorized.has_key(nick):
            ch = Registry.authorized[nick]['channel']
            greet_msg = regex.group(1)
            set_room_option(self.factory.network, ch, \
                    'greet_message', greet_msg)
            self.msg(chan, "Greet message for %s set to \"%s\" " % (ch,greet_msg))  
                  
    def set_trigger(self, regex, **kwargs):
        nick = kwargs['nick'] 
        chan = kwargs['channel']
        if Registry.authorized.has_key(nick): 
            # Command issued to bot to change the default activation
            # character.
            arg = regex.group(1)
            ch = Registry.authorized[nick]['channel'].lower()
            set_room_option(self.factory.network, ch, \
                'activation', arg)  

            self.msg(chan, "Trigger for room %s set to \"%s\"" % (ch,  arg))
            # Don't send this message twice if chan,ch are same room
            if chan != ch:
                self.msg(ch, "Trigger has been changed to \"%s\"" % (arg,)) 
                                  
    def cmd(self, regex, **kwargs):
        nick = kwargs['nick'] 
        chan = kwargs['channel']
        if nick in Registry.sys_authorized:
            # Have the bot issue any IRC command
            
            line = regex.group(1)
            logger.info("%s issued command '%s' to bot" % (nick, line))
            self.sendLine(line)
            
    def version(self, regex, **kwargs):
        nick = kwargs['nick'] 
        chan = kwargs['channel']
        dj_ver = ".".join(map(lambda x: str(x), django.VERSION[0:3]))
        pyver = (sys.version_info.major, sys.version_info.minor)
        py_ver = ".".join(map(lambda x: str(x), pyver))
        twstver = (twisted.version.major, twisted.version.minor)
        twst_ver = ".".join(map(lambda x: str(x), twstver))
        self.msg(chan, "\x033Logos Super Bot -- Version %s \x03" % (VERSION,))
        self.msg(chan, "\x0310--- Courtesy of\x03\x0312 SplatsCreations\x03")        
        self.msg(chan, "\x0310--- Built with Django %s\\Python %s\\Twisted %s  \x03" % (dj_ver, py_ver, twst_ver))        

        self.msg(chan, "\x1f\x0312https://github.com/kiwiheretic/logos-v2/")        
        
    def auth(self, regex, **kwargs):
        nick = kwargs['nick'] 
        chan = kwargs['channel']
        ch = "#" + regex.group(1).lower()
        pw = regex.group(2).strip()
        db_pw = get_room_option(self.factory.network, ch, 'password')
        nicks_in_room = self.irc_conn.get_room_nicks(ch)                                                               
        if not nicks_in_room: # if it is None then we are not in room
            self.msg(chan, 'The bot must be in room %s to authorize' % (ch,))
            return
        # room password for the bot
        # You can only authorize into the bot if you 
        # are currently in the room you are authorizing for
        if nick in nicks_in_room:
            # check password matches the one in database
            if db_pw == pw:
                if Registry.authorized.has_key(nick):
                    Registry.authorized[nick]['channel'] = ch
                else:
                    Registry.authorized[nick]={'channel':ch}
                
                self.msg(chan, '** Authorized **')
                return True
            else:
                self.msg(chan, 'Authorization Failure')
        else:
            self.msg(chan, 'You must be in room %s to authorize' % (ch,))
    
    def logout(self, regex, **kwargs):
        nick = kwargs['nick'] 
        chan = kwargs['channel']
        if nick in Registry.authorized:
            del Registry.authorized[nick]
            self.msg(chan, 'You have logged out')
        else:
            self.msg(chan, 'You were not logged in')
            
    def sysauth(self, regex, **kwargs):
        nick = kwargs['nick'] 
        chan = kwargs['channel']
        pw = regex.group(1).strip()
        
        if pw == self.factory.sys_password:
            # check to see whether nick is in control room.  You
            # can only system administrator authorise if in the 
            # engine room.
            if nick in self.get_room_nicks(self.factory.channel):
                self.msg(chan, '** Authorized **')
                logger.info( "%s sys authorized the bot" % (nick,))

                if nick not in Registry.sys_authorized:
                    Registry.sys_authorized.append(nick)
            else:
                self.msg(chan, "** You must be in the control room to system authorize **")
        else:
            self.msg(chan, 'Authorization Failure' )

            logger.info( "%s failed to sys authorize the bot" % (user,))

    def syslogout(self, regex, **kwargs):
        nick = kwargs['nick'] 
        chan = kwargs['channel']
        if nick in Registry.sys_authorized:
            Registry.sys_authorized.remove(nick)
            self.msg(chan, 'You have logged out')
            logger.info( "%s logged out from the bot" % (nick,))
        else:
            self.msg(chan, 'You were not logged in')

    def set_password(self, regex, **kwargs):
        nick = kwargs['nick'] 
        chan = kwargs['channel']
        if nick in Registry.authorized:
            pw = regex.group(1)
            ch = Registry.authorized[nick]['channel']
            set_room_option(self.factory.network, ch, \
                'password', pw)                    

            self.msg(chan, "Password for room %s set to %s " % (ch, pw))
                                 
    def command(self, nick, user, chan, orig_msg, msg, act):
        eval_mch  = re.match(act + 'eval\s+(.+)', orig_msg)
        speak_mch = re.match(act+'say\s+(.*)', msg)

        # Now we check if a system administrator command is
        # being issued to bot
        if nick in Registry.sys_authorized:
            if speak_mch:
                text = speak_mch.group(1)
                rooms = self.nicks_in_room.keys()
                for rm in rooms:
                    self.msg(rm, text)
                    
                return

            elif eval_mch:
                #
                # Have the bot issue any arbitrary python command. 
                # WARNING WARNING WARNING!!!! 
                # This is mainly used for testing and debugging and 
                # should eventually be disabled.  
                # This is because it is a MAJOR backdoor 
                # security issue.  Comment out this whole elif block
                # before final release
                eval_str = eval_mch.group(1)
                try:
                    res = repr(eval(eval_str))
                except Exception as ex:
                    res = ex.args[0]
                self.msg(chan, res)
                return True



    def signedOn(self):
        pass

    def joined(self, channel):
        # Add basic options to room setup
        defaults = ( ('activation', '!'),
                ( 'password', 'password' ),
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
        
