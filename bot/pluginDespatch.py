import os
import re
import sys
import inspect
import logging
import bot
import pdb
from django.conf import settings

from logos.models import NetworkPermissions, RoomPermissions, \
    Plugins, NetworkPlugins, RoomPlugins
from guardian.shortcuts import get_objects_for_user

logger = logging.getLogger(__name__)
logging.config.dictConfig(settings.LOGGING)

class CommandException(Exception):
    def __init__(self, user, chan, msg):
        self.user = user
        self.chan = chan
        self.msg = msg
    def __str__(self):
        return repr(self.user + ':' + self.chan + ':' + self.msg)

class AuthenticatedUsers(object):
    def __init__(self):
        self.users = []
    
    def set_password(self, nick, pw):
        user = None
        for d in self.users:
            if nick.lower() == d['nick']:
                user = d['object']
                break
        if user:
            user.set_password(pw)
            user.save()
            return True
        else:
            return False
        
    def is_authenticated(self, nick):
        user = None
        for d in self.users:
            if nick.lower() == d['nick']:
                user = d['object']
                break
        if user:
            return True
        else:
            return False
        
    def is_authorised(self, nick, network, chan, capability):
        user = None
        for d in self.users:
            if nick.lower() == d['nick']:
                user = d['object']
                break
        if not user:
            return False

        # Test if user is a net_admin and if so they always
        # have the capability
        try:
            net_perm = NetworkPermissions.objects.get(network=network)
        except NetworkPermissions.DoesNotExist:
            net_perm = None
        if net_perm:
            qs = get_objects_for_user(user, "net_admin", NetworkPermissions)
            if qs.filter(network=network).exists():
                return True

        
        if chan == '#':
           
            qs = get_objects_for_user(user, capability, NetworkPermissions)
            permission = qs.filter(network=network).exists()
            return permission
        else:
            # Test if user is a room_admin for the room in question
            # and if so they always have the capability
            try:
                room_perm = RoomPermissions.objects.get(network=network, room=chan.lower())
            except RoomPermissions.DoesNotExist:
                return False
            qs = get_objects_for_user(user, 'room_admin', RoomPermissions)
            permission = qs.filter(network=network, room=chan.lower()).exists()
            if permission:
                return True
            
            qs = get_objects_for_user(user, capability, RoomPermissions)
            permission = qs.filter(network=network, room=chan.lower()).exists()
            return permission
          
    def add(self, nick, host, user):
        self.remove(nick)
        self.users.append({'nick':nick.lower(), 'host':host, 'object':user})
    
    def remove(self, nick):
        new_list = []
        for d in self.users:
            if nick.lower() != d['nick']:
                new_list.append(d)
        self.users = new_list

    def rename(self, old, new):
        new_list = []
        for d in self.users:
            if old.lower() == d['nick']:
                d['nick'] = new.lower()
                new_list.append(d)
        self.users = new_list
        
class Plugin(object):
    """ Base Class for all plugins """
    def __init__(self, despatcher, irc_conn):
        self.irc_conn = irc_conn
        self.despatcher = despatcher
        self.factory = irc_conn.factory
        self.reactor = self.factory.reactor
        self.network = irc_conn.factory.network
        self.control_room = irc_conn.factory.channel
        
    def get_nickname(self):
        return self.irc_conn.nickname
    
    def get_host(self, nick):
        return self.irc_conn.nicks_db.get_host(nick)
    
    def get_room_nicks(self, room):
        return self.irc_conn.get_room_nicks(room)

    def get_auth(self):
        return self.despatcher.authenticated_users
    
    def enable_plugin(self, channel, plugin_name):
        return self.despatcher.enable_plugin(channel, plugin_name)
        

    def disable_plugin(self, channel, plugin_name):
        return self.despatcher.disable_plugin(channel, plugin_name)        
        
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
        self.authenticated_users = AuthenticatedUsers()
        NetworkPlugins.objects.filter(network=self.irc_conn.factory.network).update(loaded=False)
        dirs = os.listdir(settings.BASE_DIR + os.sep + os.path.join('bot', 'plugins'))
        for m in dirs:
            if m == '__init__.py' : continue
            if m[0] == '_': continue  #ignore private files
            if m[-3:] != '.py': continue  # exclude .pyc and other files
            try:
                m = re.sub(r'\.py', '', m)
                logger.info('importing module '+'bot.plugins.'+m)
                m1 = getattr(__import__('bot.plugins.'+m), 'plugins')
                mod = getattr(m1, m)

                for attr in dir(mod):
                    a1 = getattr(mod, attr)
                    # Check if the class is a class derived from 
                    # bot.PluginDespatch.Plugin
                    # but is not the base class only

                    if inspect.isclass(a1) and \
                    a1 != bot.pluginDespatch.Plugin and \
                    issubclass(a1, Plugin) and \
                    hasattr(a1, 'plugin'):  
                        logger.info('loading module '+'bot.plugins.'+m)
                        plugin_object = a1(self, irc_conn)
                        self._cls_list.append(plugin_object)
                        plugin_name, descr = plugin_object.plugin
                        plugin, created = Plugins.objects.\
                            get_or_create(name=plugin_name,
                                          description=descr)
                        net_plugin, created = NetworkPlugins.objects.\
                            get_or_create(plugin=plugin,
                                network=self.irc_conn.factory.network,
                                defaults={'loaded': True})
                        
                        if hasattr(plugin_object,'system') and \
                            plugin_object.system:
                            net_plugin.enabled = True
                        else:
                            if created:
                                net_plugin.enabled = False

                        net_plugin.loaded = True
                        net_plugin.save()    
                        
                        break
            except ImportError, e:
                logger.error("ImportError: "+str(e))

        logger.debug(str(self._cls_list))

    def enable_plugin(self, channel, plugin_name):
        if channel[0] =='#':
            try:
                room_plugin = RoomPlugins.objects.get(\
                    net__plugin__name=plugin_name,
                    net__network = self.irc_conn.factory.network,
                    room=channel)
                room_plugin.enabled = True
                room_plugin.save()
                return True
            except RoomPlugins.DoesNotExist:
                return False
        else:
            return False
        
    def disable_plugin(self, channel, plugin_name):
        if channel[0] =='#':
            for m in self._cls_list:
                m_plugin_name, _ = m.plugin
                if plugin_name == m_plugin_name:
                    if hasattr(m, 'system') and m.system:
                        # cannot disable a system plugin
                        return False
                    else:
                        try:
                            room_plugin = RoomPlugins.objects.get(\
                                net__plugin__name=plugin_name,
                                net__network = self.irc_conn.factory.network,
                                room=channel)
                            room_plugin.enabled = False
                            room_plugin.save()
                            return True
                        except RoomPlugins.DoesNotExist:
                            return False    

                    break
        else:
            return False            
    
                                   
    def install_plugin(self, channel, plugin_name, enabled=False):
        if channel[0] =='#':
            net_plugin = NetworkPlugins.objects.get(\
                            plugin__name=plugin_name,
                            network=self.irc_conn.factory.network)
                                                    
            room_plugin, created = RoomPlugins.objects.get_or_create(\
                                        net=net_plugin,
                                        room=channel.lower())
            if created:
                room_plugin.enabled = enabled
                room_plugin.save()
    
    def is_plugin_enabled(self, channel, plugin_module):
        if channel[0]=='#':
            plugin_name, _ = plugin_module.plugin
           
            try:
                obj = RoomPlugins.\
                    objects.get(net__network = self.irc_conn.factory.network,
                                room = channel.lower(),
                                net__plugin__name = plugin_name)
                        
                # system plugins are always enabled
                if obj.enabled or \
                    (hasattr(plugin_module, 'system') and plugin_module.system):
                    return True
                else:
                    return False
            except RoomPlugins.DoesNotExist:
                return False
        else:
            # currently all loaded modules are enabled in pm
            return True

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
            if self.is_plugin_enabled(channel, m):
                if hasattr(m, 'userJoined'):
                    m.userJoined(user, channel)


    def userLeft(self, user, channel):
        for m in self._cls_list:
            if self.is_plugin_enabled(channel, m):
                if hasattr(m, 'userLeft'):
                    m.userLeft(user, channel)


    def userQuit(self, user, quitMessage):
        for m in self._cls_list:
            if hasattr(m, 'userQuit'):
                m.userQuit(user, quitMessage)


    def noticed(self, user, channel, message):
        for m in self._cls_list:
            if self.is_plugin_enabled(channel, m):
                if hasattr(m, 'noticed'):
                    m.noticed(user, channel, message)


    def privmsg(self, user, channel, message):
        for m in self._cls_list:
            if self.is_plugin_enabled(channel, m): 
                if hasattr(m, 'privmsg'):
                    logger.debug("Invoking privmsg of module " + str(m))
                    m.privmsg(user, channel, message)


    def command(self, nick, user, chan, orig_msg, msg, act):

        try:
            kwargs = {'trigger':act,
                      'line': msg,
                      'user': user, # full nick@host
                      }
            
            matched_fn = []
            for m in self._cls_list:
                if self.is_plugin_enabled(chan, m): 
                    if hasattr(m, 'commands'):
                        for rgx_s, f, _ in m.commands:
                            regex = re.match(rgx_s, msg)
                            plugin_id = m.plugin[0]
                            s = plugin_id + "\s+" + rgx_s
                            regex2 = re.match(s, msg)
                            if regex2:
                                # clean_line is line without the plugin id
                                kwargs['clean_line'] = re.sub(plugin_id + "\s+", "", msg)
                                f(regex2, chan, nick, **kwargs)
                                return
                            elif regex:
                                kwargs['clean_line'] = msg
                                logger.debug('matching %s regex = %s' % (str(m.plugin), s))
                                matched_fn.append((f, regex, m.plugin))
                                
            # === Undernet Hack? ====
            # IRC servers seems to pass chan as nickname of bot's name
            # so we try to reverse this here.
            if (self.irc_conn.nickname == chan) or \
                (len(chan) == 12 and chan.lower() in self.irc_conn.nickname.lower()) :
                adj_chan = nick
            else:
                adj_chan = chan
                
            # === End Hack ===
            
            # If we found the one and only regex
            if len(matched_fn) == 1:
                fn, regex, _ = matched_fn[0]
                fn(regex, adj_chan, nick, **kwargs)
            # regex not found 
            elif len(matched_fn) == 0:
                raise CommandException(nick, chan, "Command not found")
            # otherwise more than one regex was found
            else:
                # Display error message about ambiguous command here
                plugin_list = [str(act)+x[2][0] + " " + msg for x in matched_fn ]
                self.irc_conn.say(adj_chan, 
                    "Ambiguous command.  Choose from one of %s" % (", ".join(plugin_list)))
            
                    
        except CommandException as e:
            self.irc_conn.queue_message('say', self.irc_conn.factory.channel, e.user + " typed: " + act + msg)
            self.irc_conn.queue_message('say', self.irc_conn.factory.channel, e.chan + ":" + e.msg)
            logger.debug('CommandException: ' + str( (e.user, e.chan, e.msg)))


    def joined(self, channel):
        for m in self._cls_list:
            plugin_name, _ = m.plugin
            if hasattr(m, 'system') and m.system:
                self.install_plugin(channel, plugin_name, enabled=True)
            else:
                if NetworkPlugins.objects.\
                    filter(plugin__name=plugin_name,
                           network=self.irc_conn.factory.network).exists():
                    self.install_plugin(channel, plugin_name, enabled=False)
                    
            if hasattr(m, 'joined'):
                if self.is_plugin_enabled(channel, m):         
                    m.joined(channel)


    def left(self, channel):
        for m in self._cls_list:
            if self.is_plugin_enabled(channel, m):
                if hasattr(m, 'left'):
                    m.left(channel)


    def userRenamed(self, oldname, newname):
        for m in self._cls_list:
            if self.is_plugin_enabled(channel, m):
                if hasattr(m, 'userRenamed'):
                    m.userRenamed(oldname, newname)
