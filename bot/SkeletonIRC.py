# SkeletonIRC

import sys
from twisted.internet import reactor, protocol
from twisted.words.protocols import irc

# LINE_RATE - The number of lines per second in IRC
LINE_RATE = 1

BOT_NAME = 'SkeletonBot'
IRC_NETWORK = '127.0.0.1' # usually something like irc.server.net
IRC_ROOM_NAME = '#room'

class IRCBot(irc.IRCClient):
    """ The class decodes all the IRC events"""

    def __init__(self):
        irc.IRCClient()

    def _get_nickname(self):
        return self.factory.nickname
    nickname = property(_get_nickname)


    def signedOn(self):
        """ After we sign on to the server we need to mark this irc
            client as a bot """

        self.channel = self.factory.channel.lower()
        print()
        print( "Signed on as %s." % (self.nickname,))
        print("server name = ",self.factory.servername)

        self.lineRate = LINE_RATE

        # Set the Bot with mode B so that it complies with Ablazenet
        # requirements
        line = "MODE " + self.nickname + " +B"
        self.sendLine(line)
        print(line)
        print()

        print("Joining room ", self.factory.channel)
        self.join(self.factory.channel) # Join the games channel on irc
        self.factory.conn = self

        
    def userJoined(self, user, channel):
        """
        Called when I see another user joining a channel.
        """
        pass
    
    def userLeft(self, user, channel):
        """
        Called when I see another user leaving a channel.
        """
        pass
    
    def userQuit(self, user, quitMessage):
        """
        Called when I see another user disconnect from the network.
        """
        pass
    
    def userRenamed(self, oldname, newname):
        """
        A user changed their name from oldname to newname.
        """
        pass
    
    def joined(self, channel):
        """ callback for when this bot has joined a channel """
        self.say(channel, "I, %s, have arrived :) " % (self.nickname,))
    
    def left(self, channel):
        """ Called when bot leaves channel """
        pass
    
    def noticed(self, user, channel, message):
        """ Called when receiving a NOTICE """
        pass



    def privmsg(self, user, channel, msg):
        """ This is the ideal place to process commands from the user. """
        
        # At the moment just print a silly message in chat window
        # for testing
        self.say(channel, "Elementary my dear Watson") 
        self.describe(channel, "shakes its chains")       

    
class IRCBotFactory(protocol.ClientFactory):
    protocol = IRCBot

    def __init__(self, server, channel):
        self.channel = channel
        self.nickname = BOT_NAME
        self.conn = None  # No IRC connection yet
        self.servername = server
        print("** server = ", self.servername)

    def clientConnectionLost(self, connector, reason):
        print("Lost connection (%s), reconnecting." % (reason,))
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print("Could not connect: %s" % (reason,))


########################################################################            

def main():

    # Start the IRC Bot
    reactor.connectTCP(IRC_NETWORK, 6667, IRCBotFactory(IRC_NETWORK, IRC_ROOM_NAME))

    reactor.run()
    
# this only runs if the module was *not* imported
if __name__ == '__main__':
    main()
