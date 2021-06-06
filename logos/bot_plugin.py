# test plugin
import re
import os
import json
import types

import django
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from guardian.shortcuts import assign_perm, get_perms, remove_perm

from git import Repo
import sys
import types
from logos.constants import VERSION
from bot.logos_decorators import irc_room_permission_required, \
    irc_network_permission_required

from logos.roomlib import get_room_option, get_global_option
from bot.pluginDespatch import Plugin
from logos.roomlib import get_room_option, set_room_option, set_room_defaults,\
    set_global_option, get_user_option
    


import logging
from django.conf import settings
from logos.models import Settings

logger = logging.getLogger(__name__)
logging.config.dictConfig(settings.LOGGING)
                
class SystemCoreCommands(Plugin):
    plugin = ("system", "System Module")
    system = True
    def __init__(self, *args):
        super(SystemCoreCommands, self).__init__(*args)
        self.commands = ( \
                         (r'ping', self.ping, 'ping the bot'),
                         (r'login\s+(?P<password>\S+)$', self.login, 'Login into the bot'),
                         (r'login\s+(?P<userid>\S+)\s+(?P<password>\S+)$', self.login, 'Login into the bot'),
                         
                         (r'logout', self.logout, "Log out of bot"),
                         (r'version\s*$', self.version, "Show this bot's version info"),
                         (r'help\s*$', self.help, "Show this bot's help info"),
                         (r'list\s+plugins$', self.list_plugins, "list all plugins available"),
                         (r'list\s+plugins for (?P<room>#\S+)$', self.list_plugins_for_room, "list all plugins available"),
                         (r'enable\s+plugin\s+(?P<room>#\S+)\s+(?P<plugin>[a-z0-9_-]+)',
                          self.enable_plugin, "Enable specified plugin for room"),
                         (r'disable\s+plugin\s+(?P<room>#\S+)\s+(?P<plugin>[a-z0-9_-]+)',
                          self.disable_plugin, "Disable specified plugin for room"),
                         (r'activate\s+plugin\s+(?P<plugin>[a-z0-9_-]+)',
                          self.activate_plugin, "Enable specified plugin for room"),
                         (r'deactivate\s+plugin\s+(?P<plugin>[a-z0-9_-]+)',
                          self.deactivate_plugin, "Disable specified plugin for room"),
                         (r'list\s+(?:perms|permissions)', self.list_perms, "list all permissions available"),
                         (r'add\s+user\s+(?P<username>\S+)\s+(?P<email>[a-zA-Z0-9-]+@[a-zA-Z0-9\.-]+)\s+(?P<password>\S+)$'),
                         (r'delete\s+user\s+(?P<username>\S+)$',
                          self.deluser, 'Delete user from system'),
                         (r'add\s+user\s+(?P<username>\S+)\s+(?P<email>[a-zA-Z0-9-]+@[a-zA-Z0-9\.-]+)\s+(?P<password>\S+)$',
                          self.adduser, 'Add user to system'),
                         (r'debug\s+users', self.debugusers, 'Debug list users in system'),
                         (r'list\s+users', self.listusers, 'List users in system'),
                         (r'assign\s+(?:perm|permission)\s+(?P<perm>[a-z_]+)\s+to\s+(?P<username>[^\s]+)', self.assign_net_perms, "assign permission to username"),
                         (r'assign\s+(?:perm|permission)\s+(?P<room>#\S+)\s+(?P<perm>[a-z_]+)\s+to\s+(?P<username>[^\s]+)', self.assign_room_perms, "assign permission to username"),
                         (r'unassign\s+(?:perm|permission)\s+(?P<perm>[a-z_]+)\s+from\s+(?P<username>[^\s]+)', self.unassign_net_perms, "assign permission to username"),
                         (r'unassign\s+(?:perm|permission)\s+(?P<room>#\S+)\s+(?P<perm>[a-z_]+)\s+from\s+(?P<username>[^\s]+)', self.unassign_room_perms, "assign permission to username"),
                         (r'(?:perms|permissions)\s+(?P<username>[^\s]+)', self.perms, "list permissions for user"),
                         (r'join\s+room\s+(?P<room>#\S+)', self.join_room,
                          "Request bot to join a room"),
                         (r'part\s+room\s+(?P<room>#\S+)', self.part_room,
                          "Request bot to part a room"), 
                         
                         (r'cmd\s+(.*)', self.cmd, "Have bot perform an IRC command"),
                         (r'say\s+(?P<room>#\S+)\s+(.*)', self.speak, "Say something into a room"),
                         (r'act\s+(?P<room>#\S+)\s+(.*)', self.action, "perform a /me action in room"),
                         (r'set\s+(?P<room>#\S+)\s+(?:activation|trigger)\s+\"(.)\"', self.set_trigger,
                           "Set the trigger used by the bot"),
                         (r'set\s+(?:pvt|private)\s+(?:activation|trigger)\s+\"(.)\"', self.set_pvt_trigger,
                           "Set the trigger used by the bot"),
                         (r'set\s+(?P<room>#\S+)\s+greet\s+message\s+\"(.*)\"', self.set_greet, 
                           "Set the autogreet message"),
                         (r'set\s+password\s+(\S+)$', self.set_password, "Set your password"),
                         (r'nick\s+(?P<nick>[a-zA-Z0-9-_]+)', self.set_nick, "Set the bot nick"),
                         (r'actual\s+server\s*$', self.actual_host, "Set the bot nick"),
        )
        
    
    def privmsg(self, user, channel, message):
        what_triggers_rgx = re.search("what are (?:the|your) triggers", message, re.I)
        if what_triggers_rgx:
            chan = channel.lower()
            nick = user.nick
            # determine the trigger for this room
            room_trigger = "."
            pvt_trigger = "."
            if not pvt_trigger: pvt_trigger = "!"
            user = self.get_auth().get_user_obj(nick)
            user_trigger = get_user_option(user, "trigger")
            if user_trigger:
                msg = "Room trigger is {} private windows trigger is {} Your personal user trigger is {}".format(room_trigger,pvt_trigger, user_trigger)
            else:
                msg = "Room trigger is {} private windows trigger is {}".format(room_trigger,pvt_trigger)
            self.say(chan, msg) 


    def ping(self, regex, chan, nick, **kwargs):
        self.say(chan, "pong")

    def actual_host(self, regex, chan, nick, **kwargs):
        self.say(chan, "Actual IRC server is {}".format(self.irc_conn.actual_host))
        
    def list_plugins(self, regex, chan, nick, **kwargs):
        self.notice(nick, "=== Plugins ===")
        self.notice(nick, "   === Enabled ===")
        for net_plugin in NetworkPlugins.objects.filter(network=self.network,\
                                                        loaded=True):
            plugin_name = net_plugin.plugin.name
            descr = net_plugin.plugin.description
            enabled = net_plugin.enabled
            if enabled:
                self.notice(nick, "    {0:.<15} {1:.<30}".format(plugin_name, descr))

        self.notice(nick, "   === Disabled ===")
        for net_plugin in NetworkPlugins.objects.filter(network=self.network,\
                                                        loaded=True):
            plugin_name = net_plugin.plugin.name
            descr = net_plugin.plugin.description
            enabled = net_plugin.enabled
            if not enabled:
                self.notice(nick, "    {0:.<15} {1:.<30}".format(plugin_name, descr))
                
        
    def list_plugins_for_room(self, regex, chan, nick, **kwargs):
        room = regex.group('room')
        #room = chan.lower()
        if not self.get_auth().is_authorised(nick, room, 'enable_plugins'):
            self.notice(nick, "You are not authorised (or logged in) for this room.") 
            return
        self.notice(nick, "  === Enabled plugins for room {} ===".format(room))

        for plugin in RoomPlugins.objects.filter(net__loaded = True,
                                                 net__enabled = True, 
                                                 room = chan.lower(),
                                                 net__network=self.network):
            name = plugin.net.plugin.name
            descr = plugin.net.plugin.description
            enabled = plugin.enabled
            self.notice(nick, "      {0:.<15} {1}".format(name, enabled))
            last_room = room
                 
        self.notice(nick, "*** End of List ***")  
    
        
    @irc_room_permission_required('enable_plugins')
    def enable_plugin(self, regex, chan, nick, **kwargs):
        room = regex.group('room')
        plugin_name = re.sub('-','_',regex.group('plugin'))
        if super(SystemCoreCommands, self).enable_plugin(room, plugin_name):
            self.say(chan, "plugin enabled successfully")
        else:
            self.say(chan, "plugin could not be enabled")
                
    @irc_room_permission_required('enable_plugins')
    def disable_plugin(self, regex, chan, nick, **kwargs):
        room = regex.group('room')
        plugin_name = re.sub('-','_',regex.group('plugin'))
        if super(SystemCoreCommands, self).disable_plugin(room, plugin_name):
            self.say(chan, "plugin disabled successfully")
        else:
            self.say(chan, "plugin could not be disabled")

    @irc_network_permission_required('activate_plugins')
    def activate_plugin(self, regex, chan, nick, **kwargs):
        plugin_name = re.sub('-','_',regex.group('plugin'))
        response = super(SystemCoreCommands, self).activate_plugin(plugin_name)
        if type(response) == types.TupleType:
            enabled, msg = response
        else:
            enabled = response
            msg = None
        if enabled:
            self.say(chan, "plugin activated successfully")
        else:
            self.say(chan, "plugin could not be activated")
            if msg:
                self.say(chan, "Reason: "+msg)

    @irc_network_permission_required('activate_plugins')                
    def deactivate_plugin(self, regex, chan, nick, **kwargs):
        plugin_name = re.sub('-','_',regex.group('plugin'))
        if super(SystemCoreCommands, self).deactivate_plugin(plugin_name):
            self.say(chan, "plugin disabled at network level successfully")
        else:
            self.say(chan, "plugin could not be disabled")

    @irc_network_permission_required('bot_admin')            
    def deluser(self, regex, chan, nick, **kwargs):
        username = regex.group('username')
        try:
            user = User.objects.filter(username__iexact = username.lower())
        except User.DoesNotExist:
            self.msg(chan, "User with that username could not be found")
        else:
            user.delete()
            self.msg(chan, "User deleted from database ")
    
    
    
    @irc_network_permission_required('bot_admin')            
    def adduser(self, regex, chan, nick, **kwargs):
        username = regex.group('username')
        password = regex.group('password')
        email = regex.group('email')        
        try:
            user = User.objects.get(username__iexact = username.lower())
        except User.DoesNotExist:
            user = User(username = username.lower(), email = email)
            user.set_password(password)
            user.save()
            self.msg(chan, "User successfully created")
        else:
            self.msg(chan, "User already exists in database")

    def debugusers(self, regex, chan, nick, **kwargs):
        users = self.get_auth().users
        for user in users:
            self.say(chan, str(user))

        self.say(chan, '*** end of debug users ***')

    @irc_network_permission_required('bot_admin')                     
    def listusers(self, regex, chan, nick, **kwargs):
        self.notice(nick, "List of users....")
        for user in User.objects.all():
            self.notice(nick, "{} {}".format(user.username, user.email))
        self.notice(nick, "==== End of User List =====")

    
    def login(self, regex, chan, nick, **kwargs):
        try:
            userid = regex.group('userid')
        except IndexError:
            userid = None
        password = regex.group('password')
        host = self.get_host(nick)

        try:
            if userid:
                user = User.objects.get(username__iexact = userid.lower())
            else:
                user = User.objects.get(username__iexact = nick.lower())
        except User.DoesNotExist:
            self.say(chan, "Invalid Nick")
            return
        
        if user.check_password(password):
            self.get_auth().add(nick, host, user)
            self.say(chan, "Login successful")
            self.signal("login", {"nick":nick, "user":user })

        else:
            self.say(chan, "Login failed")

    def logout(self, regex, chan, nick, **kwargs):
        username = self.get_auth().get_username(nick)
        self.get_auth().remove(nick)
        self.say(chan, "Logged out")
        self.signal("logout", {"nick":nick, "username":username })

    def list_perms(self, regex, chan, nick, **kwargs):
        self.notice(nick, "=== Network Permissions ===")
        perm_str = ", ".join([p for p,_ in NetworkPermissions._meta.permissions])
        self.notice(nick, perm_str)

        self.notice(nick, "=== Room Permissions ===")
        perm_str = ", ".join([p for p,_ in RoomPermissions._meta.permissions])
        self.notice(nick, perm_str)

    def perms(self, regex, chan, nick, **kwargs):
        username = regex.group('username').lower()
        # if user is bot_admin or if user is inquiring about themself...
        if self.get_auth().is_authorised(nick,  '#', 'bot_admin') or \
        (username == nick.lower() and self.get_auth().is_authenticated(nick)):
            try:
                user = User.objects.get(username__iexact = username)
            except User.DoesNotExist:
                self.notice(nick, "Unknown user")
                return
            
            self.notice(nick, "=== Network Permissions ===")
            for net_obj in NetworkPermissions.objects.all():
                
                perms = get_perms(user, net_obj)
                self.notice(nick, "{} {}".format(net_obj.network,
                                                    ", ".join(perms)))
            last_perms = None
            for room_obj in RoomPermissions.objects.all():
                
                perms = get_perms(user, room_obj)
                if perms:
                    if last_perms == None:
                        self.notice(nick, "\n=== Room Permissions ===")
                    self.notice(nick, "{} {} {}".format(room_obj.network,
                                                room_obj.room,
                                                ", ".join(perms))) 
        else:
            self.msg(chan, "You are not authorised or not logged in") 


    @irc_network_permission_required('bot_admin')  
    def assign_net_perms(self, regex, chan, nick, **kwargs):
        username = regex.group('username').lower()
        try:
            user = User.objects.get(username__iexact = username)
        except User.DoesNotExist:
            self.say(chan, "Unknown user")
            return

        permission = regex.group('perm')
        perm_obj = None
        for perm, desc in NetworkPermissions._meta.permissions:
            if perm == permission:
                try:
                    perm_obj = NetworkPermissions.objects.get(network=self.network)
                except NetworkPermissions.DoesNotExist:
                    perm_obj = NetworkPermissions(network=self.network)
                    perm_obj.save()
                break
        if perm_obj:
            assign_perm(permission, user, perm_obj)
            self.say(chan, "Permission assigned successfully")
        else:
            self.say(chan, "Permission not found")
            
    @irc_network_permission_required('bot_admin')  
    def unassign_net_perms(self, regex, chan, nick, **kwargs):
        username = regex.group('username').lower()
        try:
            user = User.objects.get(username__iexact = username)
        except User.DoesNotExist:
            self.say(chan, "Unknown user")
            return

        permission = regex.group('perm')
        perm_obj = None
        for perm, desc in NetworkPermissions._meta.permissions:
            if perm == permission:
                try:
                    perm_obj = NetworkPermissions.objects.get(network=self.network)
                except NetworkPermissions.DoesNotExist:
                    perm_obj = NetworkPermissions(network=self.network)
                    perm_obj.save()
                break
        if perm_obj:
            remove_perm(permission, user, perm_obj)
            self.say(chan, "Permission removed successfully")
        else:
            self.say(chan, "Permission not found")

    @irc_network_permission_required('bot_admin')  
    def assign_room_perms(self, regex, chan, nick, **kwargs):
        room = regex.group('room')
        username = regex.group('username').lower()
        try:
            user = User.objects.get(username__iexact = username)
        except User.DoesNotExist:
            self.say(chan, "Unknown user")
            return

        permission = regex.group('perm')

        perm_obj = None
        for perm, desc in RoomPermissions._meta.permissions:
            if perm == permission:
                try:
                    perm_obj = RoomPermissions.objects.get(network=self.network, room=room.lower())
                except RoomPermissions.DoesNotExist:
                    perm_obj = RoomPermissions(network=self.network, room=room.lower())
                    perm_obj.save()                    
                break        
        if perm_obj:
            assign_perm(permission, user, perm_obj)
            self.say(chan, "Permission assigned successfully")
        else:
            self.say(chan, "Permission not found")
            
    @irc_network_permission_required('bot_admin')  
    def unassign_room_perms(self, regex, chan, nick, **kwargs):
        room = regex.group('room')
        username = regex.group('username').lower()
        try:
            user = User.objects.get(username__iexact = username)
        except User.DoesNotExist:
            self.say(chan, "Unknown user")
            return

        permission = regex.group('perm')

        perm_obj = None
        for perm, desc in RoomPermissions._meta.permissions:
            if perm == permission:
                try:
                    perm_obj = RoomPermissions.objects.get(network=self.network, room=room.lower())
                except RoomPermissions.DoesNotExist:
                    perm_obj = RoomPermissions(network=self.network, room=room.lower())
                    perm_obj.save()                    
                break        
        if perm_obj:
            remove_perm(permission, user, perm_obj)
            self.say(chan, "Permission removed successfully")
        else:
            self.say(chan, "Permission not found")

    @irc_network_permission_required('join_or_part_room')  
    def join_room(self, regex, chan, nick, **kwargs):
        room = regex.group('room')
        self.join(room)
    
    @irc_network_permission_required('join_or_part_room')  
    def part_room(self, regex, chan, nick, **kwargs):
        room = regex.group('room')
        if room.lower() in self.get_rooms():
            self.say(chan, "Leaving room {} ".format(room))
            self.part(room)
        else:
            self.say(chan, "This bot is not in that room")
           
    @irc_room_permission_required('can_speak')  
    def action(self, regex, chan, nick, **kwargs):
        room = regex.group('room')
        text = regex.group(2)
        self.describe(room, text)
        
    @irc_room_permission_required('can_speak')  
    def speak(self, regex, chan, nick, **kwargs):
        room = regex.group('room')
        text = regex.group(2)
        self.msg(room, text)

    @irc_room_permission_required('set_greeting')  
    def set_greet(self, regex, chan, nick, **kwargs):
        greet_msg = regex.group(2)
        ch = regex.group('room')
        set_room_option(self.factory.network, ch, \
                'greet_message', greet_msg)
        self.msg(chan, "Greet message for %s set to \"%s\" " % (ch, greet_msg))  
                              
    @irc_room_permission_required('change_trigger')  
    def set_trigger(self, regex, chan, nick, **kwargs):
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
                                      
    @irc_network_permission_required('change_pvt_trigger') 
    def set_pvt_trigger(self, regex, chan, nick, **kwargs):
            # Command issued to bot to change the default activation
            # character.
            arg = regex.group(1)
            set_global_option('pvt-trigger', arg)
            self.msg(chan, "Private window trigger set to \"%s\"" % (arg,))

    @irc_network_permission_required('change_nick') 
    def set_nick(self, regex, chan, nick, **kwargs):
        nick_to_set = regex.group('nick')
        self.msg(chan, "Attempting to set nick to %s" % nick_to_set)
        self.irc_conn.setNick(nick_to_set)
            
    @irc_network_permission_required('irc_cmd')
    def cmd(self, regex, chan, nick, **kwargs):
        # Have the bot issue any IRC command
        
        line = regex.group(1)
        logger.debug("%s issued command '%s' to bot" % (nick, line))
        self.sendLine(line)
            
    
    def help(self, regex, chan, nick, **kwargs):
        self.notice(nick, "Wiki: \x1f\x0312https://github.com/kiwiheretic/logos-v2/wiki")        
        self.notice(nick, "Help: \x1f\x0312https://biblebot.wordpress.com")        

                         
    def version(self, regex, chan, nick, **kwargs):

        dj_ver = ".".join(map(lambda x: str(x), django.VERSION[0:3]))
        pyver = (sys.version_info.major, sys.version_info.minor, sys.version_info.micro)
        py_ver = ".".join(map(lambda x: str(x), pyver))
        self.notice(chan, "\x033Logos Super Bot -- Version %s \x03" % (VERSION,))
        self.notice(chan, "\x0310--- Courtesy of\x03\x0312 SplatsCreations\x03")        
        self.notice(chan, "\x0310--- Built with Django %s\\Python %s\\Asyncio Networking Stack \x03" % (dj_ver, py_ver))        
        # ver_path = settings.BASE_DIR
        # f = open(os.path.join(ver_path, "version.json"),"r")
        # ver_obj = json.load(f)
        # f.close()
        repo = Repo(settings.BASE_DIR)
        sha = repo.head.ref.commit.hexsha
        self.notice(nick, "\x0310SHA = {}\x03".format(sha[:8]))
        self.notice(nick, "Repo: \x1f\x0312https://github.com/kiwiheretic/logos-v2/")        
        
    def set_password(self, regex, chan, nick, **kwargs):

        if self.get_auth().is_authenticated(nick):
            pw = regex.group(1)
            self.get_auth().set_password(nick, pw)
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

    def userLeft(self, user, channel):
        if not self.is_nick_in_rooms(user):
            self.get_auth().remove(user)
            username = self.get_auth().get_username(user)
            self.signal("logout", {"nick":user, "username":username  })
        
    def userQuit(self, user, quitMessage):
        self.get_auth().remove(user)
        username = self.get_auth().get_username(user)
        self.signal("logout", {"nick":user, "username":username  })
            
    def userRenamed(self, oldname, newname):
        self.get_auth().rename(oldname, newname)
        logger.info("renamed: {}".format(str(self.get_auth().users)))
