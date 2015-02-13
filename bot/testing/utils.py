# logos testing base class

from bot import pluginDespatch
from django.utils import unittest

class FakePlugin(object):
    def __init__(self, *args, **kwargs):
        self.irc_conn = self
        self._obj_list = [self]
        self.output = []
        if 'network_settings' in kwargs:
            settings = kwargs['network_settings']
            self.nickname = settings.get('nick')
            self.user = settings.get('user')
            self.chan = settings.get('chan')
            self.network = settings.get('network')
            self.act = settings.get('act', '!')

        
    # This will suffice as long as we're note testing enabling of plugins
    # Fix this later
    def is_plugin_enabled(self, channel, plugin_module):
        return True
    
    def say(self, channel, message):
        self.output.append(('say', channel, message))

    def msg(self, channel, message):
        self.output.append(('msg', channel, message))

    def describe(self, channel, action):
        pass

    def notice(self, user, message):
        self.output.append(('notice', channel, message))

    def kick(self, channel, user, reason=None):    
        pass

    def mode(self, chan, set, modes, limit = None, user = None, mask = None):
        pass
                
    def sendLine(self, line):
        pass

    def send_command(self, msg):
        self.output=[]
        print "testing: "+msg
        orig_msg = self.act + msg
        self.command(self.nickname, self.user, self.chan, orig_msg, msg, self.act)
        print self.output
        print "--------------------------------------------"

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
        
        initial_settings = {'nick':'testBot',
                            'user':"testBot!logos@Chatopia-530r0e.xtra.co.nz",
                            'chan':'#test',
                            'act':'!',
                            'network':'irc.server.net',
                            }
        self.plugin = self.plugin_class(network_settings = initial_settings)
        

        

