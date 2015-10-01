# logos testing base class
from __future__ import print_function, absolute_import
from bot import pluginDespatch
from django.utils import unittest
from twisted.internet import reactor

from django.contrib.auth.models import User
from logos.management.commands.admin import assignperm

class FakePlugin(object):
    def __init__(self, *args, **kwargs):
        self.irc_conn = self
        self._obj_list = [self]
        self.plugin_output = []
        
        
        initial_settings = {'nickname':'testBot',
                            'user':"testBot!logos@Chatopia-530r0e.xtra.co.nz",
                            'chan':'#test',
                            'act':'!',
                            'network':'irc.server.net',
                            }
        self.reactor = reactor 
        for k in initial_settings:
            setattr(self, k, initial_settings[k])
        self.auth_users = pluginDespatch.AuthenticatedUsers(self.network)
        
        class FakeFactory:
            pass
        self.factory = FakeFactory()
        self.factory.network = self.network
                   
    def signal(self, signal_id, data):
        """ Send a signal to other plugins"""
        pass
#        self.despatcher.signal(self, signal_id, data)    
    def get_auth(self):
        return self.auth_users       
    
    def get_host(self, nick):
        return self.user 
    # This will suffice as long as we're not testing enabling of plugins
    # Fix this later
    def is_plugin_enabled(self, channel, plugin_module):
        return True
    
    def say(self, channel, message):
        self.plugin_output.append("{} {}: {}".format('say', channel, message))

    def msg(self, channel, message):
        self.plugin_output.append("{} {}: {}".format('msg', channel, message))

    def describe(self, channel, action):
        self.plugin_output.append("{} {}: {}".format('action', channel, action))

    def notice(self, user, message):
        self.plugin_output.append("{} {}: {}".format('notice', user, message))

    def kick(self, channel, user, reason=None):    
        """Not yet implemented"""
        pass

    def mode(self, chan, set, modes, limit = None, user = None, mask = None):
        """Not yet implemented"""
        pass
                
    def sendLine(self, line):
        """Not yet implemented"""
        pass

    def send_signal(self, signal_id, data):
        self.plugin_output=[]
        data['nick'] = self.nickname
        data['chan'] = self.chan
        fn = getattr(self, 'onSignal_'+signal_id)
        fn('testing', data)
        output = "\n".join(self.plugin_output)
        return (output)
        
    def send_channel_msg(self, message):
        self.plugin_output=[]
        self.privmsg(self.nickname + "!logos@fakeuser", self.chan, message)
        output = "\n".join(self.plugin_output)
        print (output)
        print ("--------------------------------------------")
        return output
        
    def send_command(self, msg):
        self.plugin_output=[]
        orig_msg = self.act + msg
        self.command(self.nickname, self.user, self.chan, 
                     orig_msg, msg, self.act)
        output = "\n".join(self.plugin_output)
        return output

# Monkey patch for testing only
# based on http://stackoverflow.com/questions/9646187/how-to-copy-a-member-function-of-another-class-into-myclass-in-python
FakePlugin.command = pluginDespatch.PluginDespatcher.__dict__['command']
FakePlugin.privmsg = pluginDespatch.PluginDespatcher.__dict__['privmsg']

# override this class
class LogosTestCase(unittest.TestCase):
    # override plugin class
    plugin_class = FakePlugin
    
    def __init__(self, *args, **kwargs):
        super(LogosTestCase, self).__init__(*args, **kwargs)

        # Hideous Monkey Patch for testing only
        self.plugin_class.__bases__ = (FakePlugin,)
        
        # default values for most settings
        

        
        self.plugin = self.plugin_class()

    @property
    def room(self):
        return self.plugin.chan    

    def set_channel(self, channel):
        self.plugin.chan = channel
    
    def set_nick(self, new_nick):
        self.plugin.nickname = new_nick 

    def create_user(self, username, email, password):
        user = User.objects.create_user(username, email, password)
        user.save()
        return user
    
    def assign_room_permission(self, username, room, permission):
        assignperm(self.plugin.network, \
                   room, username, permission)
    
    def login(self, password):
        host = self.plugin.get_host(self.plugin.nickname)

        try:
            user = User.objects.get(username__iexact = self.plugin.nickname.lower())
        except User.DoesNotExist:
            print("Invalid Nick")
            return
        
        if user.check_password(password):
            self.plugin.get_auth().add(self.plugin.nickname, host, user)
            return user
        return None