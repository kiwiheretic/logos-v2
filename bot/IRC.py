# SkeletonIRC
import pdb
import sys
import logging
import re
import time

from simple_webserver import SimpleWeb
from simple_rpcserver import SimpleRPC

from copy import copy
from logos.roomlib import get_room_option, set_room_option, get_startup_rooms

from pluginDespatch import PluginDespatcher as Plugins
from twisted.internet import reactor, protocol
from twisted.words.protocols import irc
from twisted.internet import task

# LINE_RATE - The number of lines per second in IRC
LINE_RATE = 0.5

BOT_NAME = 'SkeletonBot'
IRC_NETWORK = '127.0.0.1' # usually something like irc.server.net
IRC_ROOM_NAME = '#room'
NICKSERV = ''
QUEUE_TIMER = 0.50

from logos.settings import LOGGING
logger = logging.getLogger(__name__)
logging.config.dictConfig(LOGGING)

class NicksDB:
    def __init__(self):
        self.nicks_in_room = {}
        self.nicks_info = {}

 
    def get_rooms(self):
        return self.nicks_in_room.keys()
        
    def get_room_nicks(self, channel):
        nick_list = []
        try:
            for nr in self.nicks_in_room[channel.lower()]:
                nick_list.append(nr['nick'])
            return nick_list
        except KeyError:
            # This can occur if the irc network has some policy
            # where unregistered bots cannot join new rooms
            return None
    def add_room(self,channel):
        # Keep a list of who is in room.  We will find out later
        # when we get a RPL_NAMREPLY response as to who is actually in room.
        self.nicks_in_room[channel.lower()] = []
        
    def nick_in_room(self, user, channel):
        for nick_info in self.nicks_in_room[channel.lower()]:
            if user.lower() == nick_info['nick'].lower():
                return True
        return False
    def bot_in_room(self, channel):
        if self.nicks_in_room.has_key(channel):
            return True
        else:
            return False

    def rename_user(self, oldname, newname):
        for room in self.nicks_in_room.keys():
            for nick_info in self.nicks_in_room[room]:
                if nick_info['nick'].lower() == oldname.lower():
                    nick_info['nick'] = newname
        assert oldname.lower() in self.nicks_info
        self.nicks_info[newname.lower()] = self.nicks_info[oldname.lower()]
        del self.nicks_info[oldname.lower()]
        
        # some servers forget nickserv info upon rename
        self.nicks_info[newname.lower()]['nickserv_approved'] = None

    def remove_room(self, channel):
        del self.nicks_in_room[channel.lower()]
    
    def remove_nick(self, user, channel):
        nickl = user.lower()
        keep_list = []
        for nick_info in self.nicks_in_room[channel.lower()]:
            nick_name = nick_info['nick']
            if nick_name.lower() != nickl:
                keep_list.append(nick_info)
        self.nicks_in_room[channel.lower()] = keep_list
        if nickl in self.nicks_info:
            del self.nicks_info[nickl]
        
    def add_nick_to_room(self, user, channel, opstatus = None):
        channel_info = {'nick': user, 'opdata': opstatus }
        nick_info = {'ident': None, 'nickserv_approved':None}
        keep_list = []
        found = False
        for nick_data in self.nicks_in_room[channel.lower()]:
            if user.lower() == nick_data['nick'].lower():
                keep_list.append(channel_info)
                found = True
            else:
                keep_list.append(nick_data)
        if not found:
            self.nicks_in_room[channel.lower()].append(channel_info)
        else:
            self.nicks_in_room[channel.lower()] = keep_list
        
        if user.lower() not in self.nicks_info:
            self.nicks_info[user.lower()] = nick_info

            
    def get_ident(self, user):
        if 'ident' in self.nicks_info[user.lower()]:
            return self.nicks_info[user.lower()]['ident']
        else:
            return None

    def set_ident(self, user, ident):
        self.nicks_info[user.lower()]['ident'] = ident
    
    def get_op_status(self, user, room):
        found = False
        for nick_data in self.nicks_in_room[room.lower()]:
            if user.lower() == nick_data['nick'].lower():
                return nick_data['opdata']
        return None
    
    def set_bot_status(self, user):
        self.nicks_info[user.lower()]['bot-status'] = True

    def get_bot_status(self, user):
        if 'bot-status' in self.nicks_info[user.lower()]:
            return True
        else:
            return False

    def get_nickserv_response(self, user):
        if 'nickserv_approved' in self.nicks_info[user.lower()]:
            return self.nicks_info[user.lower()]['nickserv_approved']
        else:
            return None

    def set_nickserv_response(self, user, approved=None):
        self.nicks_info[user.lower()]['nickserv_approved'] = approved


class IRCBot(irc.IRCClient):
    """ The class decodes all the IRC events"""

    def __init__(self):
        irc.IRCClient()
        self.plugins = None 
        self.nicks_db = NicksDB()
        self.expecting_nickserv = None

        self.timer = task.LoopingCall(self.onTimer)
        self.channel_queues = {}
        self.whois_in_progress = []
        
    def queue_message(self, channel, msg_type, msg):
        chan = channel.lower()
        if chan in self.channel_queues:
            self.channel_queues[chan].append((msg_type, msg))
        else:
            self.channel_queues[chan] = [(msg_type, msg)]
            
    def _get_nickname(self):
        return self.factory.nickname
    nickname = property(_get_nickname)

    def do_whois(self, nick):
        print "do_whois " + nick
        line = "whois " + nick
        self.sendLine(line)
        
    def get_room_nicks(self, room):
        return self.nicks_db.get_room_nicks(room)

    def onTimer(self):
        keys = self.channel_queues.keys()

        for chan in self.channel_queues:
            # If the bot is in the channel or if the message
            # is not to a channel but a private message to
            # an individual nick then proceed and send the message
            if self.nicks_db.bot_in_room(chan) or chan[0] != '#': 
                queue = self.channel_queues[chan]
                try:
                    elmt = queue.pop(0)
                    action, msg = elmt

                    if action == 'say':
                        self.say(chan, str(msg))
                    elif action == 'msg':
                        self.msg(chan, str(msg))
                    elif action == 'describe':
                        self.describe(chan, str(msg));
                    elif action == 'notice':
                        self.notice(chan, str(msg))
                    else:
                        logger.debug('action not found ' + str(elmt) )
                except IndexError:
                    pass

    def signedOn(self):
        """ After we sign on to the server we need to mark this irc
            client as a bot """

        irc.IRCClient.signedOn(self)
        self.plugins = Plugins(self)
        self.channel = self.factory.channel.lower()
        logger.info("server name = "+self.factory.network)
        logger.info( "Signed on as %s." % (self.nickname,))

        self.lineRate = LINE_RATE

        # Set the Bot with mode B so that it complies with Ablazenet
        # requirements
        line = "MODE " + self.nickname + " +B"
        self.sendLine(line)
        logger.info(line)

        if self.factory.nickserv_password:
            line = "NS IDENTIFY " + self.factory.nickserv_password
            self.sendLine(line)
            logger.info(line)

        self.factory.conn = self

        self.plugins.signedOn()

        rooms = get_startup_rooms(self.factory.network)
        for rm in rooms:
            if rm != self.factory.channel.lower():
                self.join(str(rm))
                logger.info("Joining room "+ rm)

        logger.info("Joining room "+ self.factory.channel)
        self.join(self.factory.channel)
        self.timer.start(QUEUE_TIMER)

    def userJoined(self, user, channel):
        """
        Called when I see another user joining a channel.
        """
        logger.info(user + " has joined " + channel)
        irc.IRCClient.userJoined(self, user, channel)

        if not self.nicks_db.nick_in_room(user, channel):
            self.nicks_db.add_nick_to_room(user, channel)
        self.plugins.userJoined(user, channel)
        line = "WHOIS " + user
        self.sendLine(line)
        print self.nicks_db.nicks_in_room
        print self.nicks_db.nicks_info

    def userLeft(self, user, channel):
        """
        Called when I see another user leaving a channel.
        """
        logger.info(user + " has left " + channel)
        irc.IRCClient.userLeft(self, user, channel)

        if self.nicks_db.nick_in_room(user, channel):
            self.nicks_db.remove_nick(user, channel)
        self.plugins.userLeft(user, channel)
        logger.debug( repr(self.nicks_db.nicks_in_room))
        logger.debug( repr(self.nicks_db.nicks_info))

    def userQuit(self, user, quitMessage):
        """
        Called when I see another user disconnect from the network.
        """
        logger.info(user + " has quit with message: " + quitMessage)
        irc.IRCClient.userQuit(self, user, quitMessage)

        nick = user
        rooms = self.nicks_db.get_rooms()
        for room in rooms:
            names = self.nicks_db.get_room_nicks(room)
            if nick in names:
                self.nicks_db.remove_nick(user, room)

        self.plugins.userQuit(user, quitMessage)

    def userRenamed(self, oldname, newname):
        """
        A user changed their name from oldname to newname.
        """

        logger.info(oldname + " has renamed to " + newname)
        irc.IRCClient.userRenamed(self, oldname, newname)

        self.nicks_db.rename_user(oldname, newname)
        self.plugins.userRenamed(oldname, newname)
        
        self.factory.reactor.callLater(5, self.do_whois, newname)
        logger.debug(str( self.nicks_db.nicks_in_room))
        logger.debug(str( self.nicks_db.nicks_info))
        
    def joined(self, channel):
        """ callback for when this bot has joined a channel """
        logger.info( "%s has joined %s " % ( self.factory.nickname, channel,))

        irc.IRCClient.joined(self, channel)

        # Keep a list of who is in room.  We will find out later
        # when we get a RPL_NAMREPLY response as to who is actually in room.
        self.nicks_db.add_room(channel)


        self.plugins.joined(channel)


        line = "NAMES " + channel
        self.sendLine(line)
        logger.info(line)

        act = get_room_option(self.factory.network, channel, 'activation')
        if not act: act = '!'
        self.say(channel, str("Your trigger is '%s', type %shelp for more info" % (act,act)))

        
    def left(self, channel):
        """ Called when bot leaves channel """
        irc.IRCClient.left(self, channel)
        logger.info("The bot has left " + channel)
        self.nicks_db.remove_room(channel)
        if channel != self.factory.channel:
            self.say(self.factory.channel, "%s has left channel %s" %
                ( self.factory.nickname, channel,))

        self.plugins.left(channel)


    def noticed(self, user, channel, message):
        """ Called when receiving a NOTICE """
        irc.IRCClient.noticed(self, user, channel, message)
        logger.info('Notice Received : ' + user + ' ' + channel + ' ' + message)
        nick = user.split('!')[0].lower()
        if nick == "nickserv":

            mch = re.search('([^\s]+) is not registered', message)
            if mch:
                user = mch.group(1)
                user = re.sub('\x02', '', user)
                # channel is user here as this is used
                # when we receive a notice from a single user
                self.nicks_db.set_nickserv_response(user, approved=False)
            mch = re.search('Information on\s+([^\s]+)', message)
            if mch:
                user = mch.group(1)
                user = re.sub('\x02', '', user)
                self.expecting_nickserv = user
                print "got here"
            mch = re.search("(\w+)\W+is part of this Network's Services", message)
            if mch:
                user = mch.group(1)
                self.nicks_db.set_bot_status(user)
            if re.search('Last seen\s+: now', message, re.I):  
                if self.expecting_nickserv:
                    self.nicks_db.set_nickserv_response(self.expecting_nickserv, 
                                                        approved=True) 
                    self.expecting_nickserv = None
                    print self.nicks_db.nicks_in_room
                    print self.nicks_db.nicks_info                                
        if self.plugins:
            self.plugins.noticed(user, channel, message)
#        elif self.factory:
#            self.queue_message(self.factory.channel, 'say', user + ": " + message )

            


    def privmsg(self, user, channel, orig_msg):
        """ This is the ideal place to process commands from the user. """
        #logger.debug( "%s on %s says %s " % ( user, channel, orig_msg))

        irc.IRCClient.privmsg(self, user, channel, orig_msg)

        # Strip out the mIRC colour codes on incoming commands.
        # This makes the bot colour tolerant and won't reject commands
        # if they are not in only black.
        msg = orig_msg
        msg = re.sub('\x02|\x16|\x1F|\x1D', '', msg)
        msg = re.sub('\x03\d+,\d+', '', msg)
        msg = re.sub('\x03\d+', '', msg)
        msg = re.sub('\x03', '', msg)

        # strip out leading and trailing spaces
        msg = msg.strip()
        # ... and make all lower case for easy pattern matching
        #msg = msg.lower()

        act = get_room_option(self.factory.network, channel, 'activation')
        if not act: act = '!'

        # if we wish to return a self.msg(...) to an incoming command
        # we need to send it to a nickname if the message was private
        # or to the channel if it was public.  The problem with the 'channel'
        # parameter is that is shows the sender (not the recipient) in the context
        # of a private message.  Hence the need to set the chan variable below.
        if channel == self.factory.nickname:
            chan = user.split('!')[0]
        else:
            chan = channel.lower()

        # set the nick variable for use with self.msg(...) as user,
        # as an argument, doesn't work.  
        nick = user.split('!')[0]
        mch = re.match(re.escape(act)+ "(.*)", msg)
        if mch:
            msg = mch.group(1).strip()
            self.plugins.command(nick, user, chan, orig_msg, msg, act)

        self.plugins.privmsg(user, channel, orig_msg)
    
    def irc_unknown(self, prefix, command, params):
        """ Used to handle RPL_NAMREPLY and REL_WHOISUSER events
            so that we can keep a track of who is and who isn't
            in channel.  Particularly useful for when the bot
            enters a channel with people already on it."""
        irc.IRCClient.irc_unknown(self, prefix, command, params)

        line =  '[u]: ' + prefix + ',' + command + ',' + ','.join(params)
        if command not in ['PONG']: # we don't care about these
            logger.debug(line)
#            self.queue_message(self.factory.channel, 'say', line)

        # We use the RPL_NAMREPLY to get a list of all people currently
        # in a room when the bot first joins that room and uses that information
        # to populate the self._nicks_in_room dictionary.

        if command == "335":
            logger.debug("335 " +  str(params))
            user = params[1]
            bot_status = params[2]

            if re.search("bot", bot_status, re.I):
                self.nicks_db.set_bot_status(user)
        elif command == "307":
            logger.debug("307 " +  str(params))
            user = params[1]
            self.nicks_db.set_nickserv_response(user, approved = True)
        elif command == "RPL_NAMREPLY":
            room = params[2].lower()
            if room not in self.whois_in_progress:
                names = params[3].strip().split(' ')
                for name in names:

                    if name == '': continue
                    this_name = name


                    # strip off nickname prefixes for ops and voice
                    opstatus = None
                    if this_name[0] in "~%&@+":
                        opstatus = this_name[0]
                        this_name = this_name[1:]



                    if not self.nicks_db.nick_in_room(this_name, room):
                        self.nicks_db.add_nick_to_room(this_name, room, opstatus=opstatus)
                        ident = self.nicks_db.get_ident(this_name)
                        if ident == None:
                            # need to strip opstatus off first
                            if this_name not in self.whois_in_progress:
                                self.whois_in_progress.append(this_name)
                            else:
                                continue # don't do whois twice on same nick                            
                            line = "whois " + this_name
                            self.sendLine(line)
                
        elif command == "RPL_WHOISUSER":
            user = params[1]
            ident = params[3]
            if user in self.whois_in_progress:
                self.whois_in_progress.remove(user)
                self.nicks_db.set_ident(user, ident)
                line = 'privmsg nickserv info ' + user
                self.sendLine(line)


class IRCBotFactory(protocol.ClientFactory):
    protocol = IRCBot

    def __init__(self, reactor, server, channel, nickname,  \
                 sys_password, nickserv_pw, web_port, rpc_port):
        
        self.reactor = reactor
        self.channel = channel
        self.web_port = web_port
        self.rpc_port = rpc_port
        self.nickname = nickname
        self.conn = None  # No IRC connection yet
        self.network = server
        self.nickserv_password = nickserv_pw
        self.sys_password = sys_password
        
        if web_port:
            self.web = SimpleWeb(reactor, self, web_port)
        else:
            self.web = None
            
        if rpc_port:
            self.rpc = SimpleRPC(reactor, self, rpc_port)
        else:
            self.rpc = None

   
    def doReconnect(self, connector):
        logging.info("Attempting to reconect to server...")
        connector.connect()
        
    def clientConnectionLost(self, connector, reason):
        logging.info("Lost connection (%s), will reconnect shortly..." % (reason,))
        # Taken from https://twistedmatrix.com/documents/13.1.0/core/howto/time.html
        self.reactor.callLater(3, self.doReconnect, connector)


    def clientConnectionFailed(self, connector, reason):
        logging.info("Could not connect: %s, will reconnect in 10 seconds" % (reason,))
        self.reactor.callLater(10, self.doReconnect, connector)


########################################################################

def instantiateIRCBot(network, port, room, botName, sys_password, 
                      nickserv, web_port = None, rpc_port=None):

    # Start the IRC Bot
    reactor.connectTCP(network, port,
                       IRCBotFactory(reactor, network, room, botName,\
                                     sys_password, nickserv, web_port, rpc_port))

    
    reactor.run()

def main():
    instantiateIRCBot(IRC_NETWORK, 6667, IRC_ROOM_NAME, BOT_NAME, NICKSERV)

# this only runs if the module was *not* imported
if __name__ == '__main__':
    main()
