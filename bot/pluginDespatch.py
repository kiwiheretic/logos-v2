import os
import re
import sys
import inspect
import logging
import bot
import pdb
from logos.settings import PROJECT_ROOT_DIR, LOGGING

logger = logging.getLogger(__name__)
logging.config.dictConfig(LOGGING)

class CommandException(Exception):
    def __init__(self, user, chan, msg):
        self.user = user
        self.chan = chan
        self.msg = msg
    def __str__(self):
        return repr(self.user + ':' + self.chan + ':' + self.msg)


class Plugin(object):
    """ Base Class for all plugins """
    def __init__(self, dispatcher, irc_conn):
        self.irc_conn = irc_conn
        self.dispatcher = dispatcher
        self.factory = irc_conn.factory
        self.reactor = self.factory.reactor
        self.network = irc_conn.factory.network
        self.control_room = irc_conn.factory.channel
        
    def get_ident(self, nick):
        return self.irc_conn.nicks_db.get_ident(nick)
    
    def get_room_nicks(self, room):
        return self.irc_conn.get_room_nicks(room)

    def signal(self, scope, message_id, *args):
        self.dispatcher.signal_plugins(self, scope, message_id, *args)
        

    
#    def __getattr__(self, name):
#        if hasattr(self.irc_conn, name):
#            attr = getattr(self.irc_conn, name)
#            # fudge a closure in python 2.7 using a dictionary
#            # see http://technotroph.wordpress.com/2012/10/01/python-closures-and-the-python-2-7-nonlocal-solution/
#            d = {'conn': self.irc_conn}
#            if hasattr(attr, "__call__"):
#                def method_dispatcher(self, *args, **kwargs):
#                    d['conn'].queue_message(*args, **kwargs)
#                return method_dispatcher
#            else:
#                raise AttributeError
                    
                
            
    def say(self, channel, message):
        if channel[0] == '#':
            self.irc_conn.queue_message('say', channel, message)
        else:
            self.irc_conn.queue_message('msg', channel, message)

    def msg(self, channel, message):
        self.irc_conn.queue_message('msg', channel, message)

    def describe(self, channel, action):
        self.irc_conn.queue_message('describe', channel, action)

    def notice(self, user, message):
        self.irc_conn.queue_message('notice', user, message)

    def kick(self, channel, user, reason=None):    
        self.irc_conn.queue_message('kick', channel, user, reason)

    def mode(self, chan, set, modes, limit = None, user = None, mask = None):
        """
        Change the modes on a user or channel.

        The C{limit}, C{user}, and C{mask} parameters are mutually exclusive.

        @type chan: C{str}
        @param chan: The name of the channel to operate on.
        @type set: C{bool}
        @param set: True to give the user or channel permissions and False to
            remove them.
        @type modes: C{str}
        @param modes: The mode flags to set on the user or channel.
        @type limit: C{int}
        @param limit: In conjuction with the C{'l'} mode flag, limits the
             number of users on the channel.
        @type user: C{str}
        @param user: The user to change the mode on.
        @type mask: C{str}
        @param mask: In conjuction with the C{'b'} mode flag, sets a mask of
            users to be banned from the channel.
        """        
        self.irc_conn.queue_message('mode', chan, set, modes, limit, user, mask)
                
    def sendLine(self, line):
        self.irc_conn.sendLine(line)
        
class PluginDespatcher(object):
    """ Handles method delegation to the .py files in the plugins
    folder. Its been created with a whole lot of static methods because
    we want this class to act like a singleton"""
    _cls_list = []
    factory = None

    def __init__(self, irc_conn):
        """ This imports all the .py files in
        the plugins folder """
        
        self.irc_conn = irc_conn
                
        dirs = os.listdir(PROJECT_ROOT_DIR + os.sep + os.path.join('bot', 'plugins'))
        for m in dirs:
            if m == '__init__.py' : continue
            if m[0] == '_': continue  #ignore private files
            if m[-3:] != '.py': continue  # exclude .pyc and other files
            try:
                m = re.sub(r'\.py', '', m)

                m1 = getattr(__import__('bot.plugins.'+m), 'plugins')
                mod = getattr(m1, m)

                for attr in dir(mod):
                    a1 = getattr(mod, attr)
                    # Check if the class is a class derived from 
                    # bot.PluginDespatch.Plugin
                    # but is not the base class only
                    if inspect.isclass(a1) and \
                    a1 != bot.pluginDespatch.Plugin and \
                    issubclass(a1, Plugin):  
                        logger.info('loading module '+'bot.plugins.'+m)
                        self._cls_list.append(a1(self, irc_conn))
                        break
            except ImportError, e:
                logger.error("ImportError: "+str(e))

        logger.debug(str(self._cls_list))

    
    def signal_plugins(self, sender, scope, msg_id, *args):
        # currently not used
        for cls in self._cls_list:
            if cls != sender:
                if hasattr(cls, 'onSignal'):
                    cls.onSignal(scope, msg_id, *args)
            
    
    # ---- delegate methods below --------

    # Possible TODO
    # Look at using __getattr__ for these following methods and dynamically
    # creating the methods.  What are the advantages?  More DRY.

    def signedOn(self):
        for m in self._cls_list:
            #m.init(self)
            if hasattr(m, 'signedOn'):
                m.signedOn()


    def userJoined(self, user, channel):
        for m in self._cls_list:
            if hasattr(m, 'userJoined'):
                m.userJoined(user, channel)


    def userLeft(self, user, channel):
        for m in self._cls_list:
            if hasattr(m, 'userLeft'):
                m.userLeft(user, channel)


    def userQuit(self, user, quitMessage):
        for m in self._cls_list:
            if hasattr(m, 'userQuit'):
                m.userQuit(user, quitMessage)


    def noticed(self, user, channel, message):
        for m in self._cls_list:
            if hasattr(m, 'noticed'):
                m.noticed(user, channel, message)


    def privmsg(self, user, channel, message):
        for m in self._cls_list:
            if hasattr(m, 'privmsg'):
                logger.debug("Invoking privmsg of module " + str(m))
                m.privmsg(user, channel, message)


    def command(self, nick, user, chan, orig_msg, msg, act):
        pri_list = {}
        priorities = ('system', 'high', 'normal', 'low')

        for m in self._cls_list:
            if hasattr(m, 'priority'):
                pri = m.priority
                if pri not in priorities: pri = 'normal'
            else:
                pri = 'normal'
            if pri in pri_list:
                pri_list[pri].append(m)
            else:
                pri_list[pri] = [m]
                
        
        for p in priorities:
            if p in pri_list:
                for m in pri_list[p]:
                    if hasattr(m, 'command'):
                        try:
                            completed = m.command(nick, user, chan, orig_msg, msg, re.escape(act))
                            if completed:
                                return
                        except CommandException as e:
                            self.irc_conn.queue_message('say', self.irc_conn.factory.channel, e.user + " typed: " + act + msg)
                            self.irc_conn.queue_message('say', self.irc_conn.factory.channel, e.chan + ":" + e.msg)
                            logger.debug('CommandException: ' + str( (e.user, e.chan, e.msg)))


    def joined(self, channel):
        for m in self._cls_list:
            if hasattr(m, 'joined'):
                m.joined(channel)


    def left(self, channel):
        for m in self._cls_list:
            if hasattr(m, 'left'):
                m.left(channel)


    def userRenamed(self, oldname, newname):
        for m in self._cls_list:
            if hasattr(m, 'userRenamed'):
                m.userRenamed(oldname, newname)
