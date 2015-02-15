# logos testing base class

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
        pass

    def notice(self, user, message):
        self.plugin_output.append("{} {}: {}".format('notice', channel, message))

    def kick(self, channel, user, reason=None):    
        pass

    def mode(self, chan, set, modes, limit = None, user = None, mask = None):
        pass
                
    def sendLine(self, line):
        pass

    def send_command(self, msg):
        self.plugin_output=[]
        print "testing: "+msg
        orig_msg = self.act + msg
        self.command(self.nickname, self.user, self.chan, 
                     orig_msg, msg, self.act)
        output = "\n".join(self.plugin_output)
        print output
        print "--------------------------------------------"
        return output

# Monkey patch for testing only
# based on http://stackoverflow.com/questions/9646187/how-to-copy-a-member-function-of-another-class-into-myclass-in-python
FakePlugin.command = pluginDespatch.PluginDespatcher.__dict__['command']

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

    def set_nick(self, new_nick):
        self.plugin.nickname = new_nick 

    def create_user(self, username, email, password):
        user = User.objects.create_user(username, email, password)
        user.save()
    
    def assign_room_permission(self, username, room, permission):
        assignperm(self.plugin.network, \
                   room, username, permission)
    
    