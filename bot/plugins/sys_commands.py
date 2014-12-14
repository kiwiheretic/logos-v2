# test plugin
import re
import pdb

import django
import twisted
import sys
from logos.constants import VERSION

from bot.pluginDespatch import Plugin
from logos.roomlib import get_room_option, set_room_option, set_room_defaults
from logos.pluginlib import Registry

import logging
from logos.settings import LOGGING

logger = logging.getLogger(__name__)
logging.config.dictConfig(LOGGING)

class SystemCommandsClass(Plugin):
    priority="system"
    
    def __init__(self, *args):
        super(SystemCommandsClass, self).__init__(*args)
        Registry.sys_authorized = []   # List of system authorized nicks - ie owner
        Registry.authorized = {}  
    
    def privmsg(self, user, channel, message):
        pass

    def command(self, nick, user, chan, orig_msg, msg, act):
        sysauth_mch = re.match('sysauth\s(.+)', msg)
        syslogout_mch = re.match('syslogout', msg)

        eval_mch  = re.match(act + 'eval\s+(.+)', orig_msg)
        auth_mch = re.match('auth\s+#(#?[a-zA-Z0-9_-]+)\s+(.+)', msg)
        logout_mch = re.match('logout', msg)
        set_password_mch = re.match(act + 'set\s+password\s+\"([^"]+)\"', orig_msg)
        
        speak_mch = re.match(act+'speak\s+(.*)', msg)
        cmd_mch = re.match(act+'cmd\s+(.*)', orig_msg)
        set_activ_mch = re.match(act+'set\s+(?:activation|trigger)\s+\"(.)\"', orig_msg)
        set_errors_mch = re.match('set\s+errors\s+(.*)', msg)
        set_greet_mch = re.match(act+'set\s+greet\s+message\s+\"(.*)\"', orig_msg)
        version_mch = re.match('version\s*$', msg)  
   
        # If a version command is issued return the version number
        # of the bot along with credits
        if version_mch:
            dj_ver = ".".join(map(lambda x: str(x), django.VERSION[0:3]))
            pyver = (sys.version_info.major, sys.version_info.minor)
            py_ver = ".".join(map(lambda x: str(x), pyver))
            twstver = (twisted.version.major, twisted.version.minor)
            twst_ver = ".".join(map(lambda x: str(x), twstver))
            self.msg(chan, "\x033Logos Super Bot -- Version %s \x03" % (VERSION,))
            self.msg(chan, "\x0310--- Courtesy of\x03\x0312 SplatsCreations\x03")        
            self.msg(chan, "\x0310--- Built with Django %s\\Python %s\\Twisted %s  \x03" % (dj_ver, py_ver, twst_ver))        

            self.msg(chan, "\x1f\x0312http://biblebot.wordpress.com/bible-bot-instructions/")        

            
            return True
        
        elif sysauth_mch:
            pw = sysauth_mch.group(1).strip()
            
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
            return True

        elif syslogout_mch:
            Registry.sys_authorized.remove(nick)
            print self.sys_authorized
            self.msg(chan, 'You have logged out')
            logger.info( "%s logged out from the bot" % (user,))
            return

        elif auth_mch:
            # If we are authorizing as a room owner then the room owner
            # can change some settings for the bot for their room only.
            ch = "#" + auth_mch.group(1).lower()
            pw = auth_mch.group(2).strip()
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

                    
        elif logout_mch:
            if nick in Registry.authorized:
                del Registry.authorized[nick]
                self.msg(chan, 'You have logged out')

        else:
            # Now we check if a system administrator command is
            # being issued to bot
            if nick in Registry.sys_authorized:
                if speak_mch:
                    text = speak_mch.group(1)
                    rooms = self.nicks_in_room.keys()
                    for rm in rooms:
                        self.msg(rm, text)
                        
                    return

                elif cmd_mch:
                    # Have the bot issue any IRC command
                    
                    line = cmd_mch.group(1)
                    logger.info("%s issued command '%s' to bot" % (user, line))
                    self.sendLine(line)
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

            # If nick has authorized a room with the bot
            if Registry.authorized.has_key(nick):
                if set_greet_mch:
                    ch = Registry.authorized[nick]['channel']
                    greet_msg = set_greet_mch.group(1)
                    set_room_option(self.factory.network, ch, \
                            'greet_message', greet_msg)
                    self.msg(chan, "Greet message for %s set to \"%s\" " % (ch,greet_msg))
                    return True
                    
                elif set_errors_mch:
                    error_status = set_errors_mch.group(1).strip().lower()
                    if error_status in ( "on", "off" ):
                        ch = self.authorized[nick]['channel']
                        set_room_option(self.factory.network, ch, \
                            'error_status', error_status)
                        self.msg(chan, "Error status for %s set to %s " % (ch,error_status))
                    else:
                        self.msg(chan, "Unknown status \"%s\", expected 'on' or 'off' " % (errors_status,))
                    return True
                elif set_password_mch:
                    pw = set_password_mch.group(1)
                    ch = Registry.authorized[nick]['channel']
                    set_room_option(self.factory.network, ch, \
                        'password', pw)                    

                    self.msg(chan, "Password for room %s set to %s " % (ch, pw))
                    return True
                elif set_activ_mch:
                    # Command issued to bot to change the default activation
                    # character.
                    arg = set_activ_mch.group(1)
                    ch = Registry.authorized[nick]['channel'].lower()
                    set_room_option(self.factory.network, ch, \
                        'activation', arg)  
 
                    self.msg(chan, "Trigger for room %s set to \"%s\"" % (ch,  arg))
                    if chan != ch:
                        self.msg(ch, "Trigger has been changed to \"%s\"" % (arg,))
                    return

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
        
