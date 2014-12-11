# test plugin
from bot.pluginDespatch import Plugin

class TestClass(Plugin):
    def privmsg(self, user, channel, message):
        self.say(channel, "Elementary my dear Watson")
        self.describe(channel, "shakes its chains")

    def command(self, user, chan, msg, act):
        print "test-command: ", user, chan, msg, act

    def signedOn(self):
        pass

    def joined(self, channel):
        self.say(channel, "I, Logos, have arrived")

    def userRenamed(self, old, new):
        self.notice(new, "You changed your nick from %s to %s" % (old, new))

