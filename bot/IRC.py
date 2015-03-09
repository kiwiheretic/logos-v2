# SkeletonIRC
import pdb
import sys
import logging
import string
import re
import os
import types
import time
import signal
import socket

from simple_webserver import SimpleWeb
from simple_rpcserver import SimpleRPC
import logos.utils

from copy import copy
from logos.roomlib import get_room_option, set_room_option, get_startup_rooms, \
    get_global_option

from pluginDespatch import PluginDespatcher as Plugins
from twisted.internet import reactor, protocol
from twisted.words.protocols import irc
from twisted.internet import task

from django.conf import settings

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
        
    def nick_in_any_room(self, nick):
        """ Is nick in any room that the bot knows about, not
        any room on the entire network """
        for room in self.nicks_in_room.keys():
            if self.nick_in_room(nick, room):
                return True
        return False
            
    def nick_in_room(self, user, channel):
        if channel.lower() in self.nicks_in_room:
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
        if channel.lower() not in self.nicks_in_room:
            self.nicks_in_room[channel.lower()] = [channel_info]
        else:
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

            
    def get_host(self, user):
        try:
            if 'ident' in self.nicks_info[user.lower()]:
                return self.nicks_info[user.lower()]['ident']
            else:
                return None
        except KeyError:
            # This can fail on slow servers, notably undernet
            return None

    def set_ident(self, user, ident):
        logger.debug("Setting Ident for %s = %s" % (user, ident))
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

    def __init__(self, *args, **kwargs):
        irc.IRCClient(*args, **kwargs)
        self.plugins = None 
        self.nicks_db = NicksDB()
        self.expecting_nickserv = None
        self.actual_host = None

        self.timer = task.LoopingCall(self.onTimer)
        self.log_flush_timer = task.LoopingCall(self.onLogFlushTimer)
        self.log_flush_timer.start(30)
        self.channel_queues = {}
#        self.whois_in_progress = []
        self.userhost_in_progress = []

        
        # Some IRC servers seem to require username and realname
        # (notably some Undernet servers)
        self.username = "logos"
        self.realname = "logos"
        
        if settings.DEBUG:
            self.irc_line_log = open(os.path.join(settings.LOG_DIR, "IRClinesReceived.txt"), "ab")
        else:
            self.irc_line_log = None
        
        signal.signal(signal.SIGINT, self.handle_ctrl_c)
              
    def handle_ctrl_c(self, signum, frame):
        print "closing file"
        if self.irc_line_log:
            self.irc_line_log.close()
        self.factory.reactor.stop()
        self.factory.shutting_down = True
            
    def queue_message(self, msg_type, channel,  *args):
        chan = channel.lower()
        l = [msg_type, channel]
        l.extend(args)

        if chan in self.channel_queues:
            self.channel_queues[chan].append(l)
        else:
            self.channel_queues[chan] = [l]
            
    def _get_nickname(self):
        return self.factory.nickname
    nickname = property(_get_nickname)

    def do_whois(self, nick):
        logger.debug( "do_whois " + nick)
        line = "whois " + nick
        self.sendLine(line)
        
    def get_room_nicks(self, room):
        return self.nicks_db.get_room_nicks(room)

    def onLogFlushTimer(self):
        # Getting flushed file output to actually appear inside the text file
        # is hard because windows still caches the output in OS buffers even after
        # a flush().  See url below.
        # http://stackoverflow.com/questions/7127075/what-exactly-the-pythons-file-flush-is-doing
        this_logger = logging.getLogger()
        handlers = this_logger.handlers
        for handler in handlers:
            handler.flush()
            try:
                os.fsync(handler.stream.fileno())
            except OSError:
                pass
        
    def onTimer(self):
        for chan in self.channel_queues:
            # If the bot is in the channel or if the message
            # is not to a channel but a private message to
            # an individual nick then proceed and send the message

            if self.nicks_db.bot_in_room(chan) or chan[0] != '#': 
                msg_list = []
                if len(self.channel_queues[chan]) == 0:
                    continue
                chan_q = self.channel_queues[chan].pop(0)
                for elmt in chan_q:
                    if type(elmt) == types.UnicodeType:
                        msg_list.append(elmt.encode("utf-8","replace_spc"))
                    else:
                        msg_list.append(elmt)

#                logger.debug("timer: "+str((chan, msg_list)))
                action = msg_list.pop(0)
                if hasattr(self, action):
                    # sendLine used for startup script primarily
                    if action == "sendLine":
                        line = msg_list[1].strip()
                        logger.debug("Sending raw line : "+line)
                        self.sendLine(line)
                    else:
                        f = getattr(self, action)
                        args = msg_list
                        f(*args)
                else:
                    logger.debug('action not found ' + str(action) )


    def irc_RPL_YOURHOST(self, prefix, params):
        self.actual_host = prefix
        logger.info("Connected to IRC Server: {}".format(prefix))
        irc.IRCClient.irc_RPL_YOURHOST(self, prefix, params)
        
    def signedOn(self):
        """ After we sign on to the server we need to mark this irc
            client as a bot """

        irc.IRCClient.signedOn(self)
        self.plugins = Plugins(self)
        self.channel = self.factory.channel.lower()
        logger.info("Target IRC server:  "+self.factory.network)

        self.lineRate = LINE_RATE

        # Set the Bot with mode B so that it complies with Ablazenet
        # requirements
        line = "MODE " + self.nickname + " +B"
        self.sendLine(line)
        logger.info(line)

        if self.factory.nickserv_password and not self.factory.extra_options['no_services']:
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

        if self.factory.extra_options['room_key']:
            room_key = self.factory.extra_options['room_key']
            self.join(self.factory.channel, room_key)
        else:
            self.join(self.factory.channel)
        logger.info("Joining room "+ self.factory.channel)
        
        if self.factory.extra_options['startup_script']:
            try:
                f = open(self.factory.extra_options['startup_script'])
                for line in f.readlines():
                    line_repl = string.replace(line, "%nick%", self.nickname)
                    self.queue_message('sendLine', 'sendLine', line_repl)
                f.close()
            except IOError:
                pass
        self.timer.start(QUEUE_TIMER)        

    def sendLine(self, line):
        if self.irc_line_log:
            self.irc_line_log.write(">> " + repr(line)+"\n")
        irc.IRCClient.sendLine(self, line)

    def lineReceived(self, line):
        if self.irc_line_log:
           self.irc_line_log.write("<< " + repr(line) +"\n") 
        irc.IRCClient.lineReceived(self, line)
        
    def userJoined(self, user, channel):
        """
        Called when I see another user joining a channel.
        """
        logger.info(user + " has joined " + channel)
        irc.IRCClient.userJoined(self, user, channel)

        if not self.nicks_db.nick_in_room(user, channel):
            self.nicks_db.add_nick_to_room(user, channel)
        self.plugins.userJoined(user, channel)
        line = "USERHOST " + user
        self.sendLine(line)
        logger.debug(str( self.nicks_db.nicks_in_room))
        logger.debug(str( self.nicks_db.nicks_info))

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
        logger.debug(line)

        act = get_room_option(self.factory.network, channel, 'activation')
        if not act: act = '!'
        pvt_act = get_global_option('pvt-trigger')
        if not pvt_act: pvt_act = "!"
        self.msg(channel, str("Bot initialised, Your trigger is '%s', private chat trigger is \"%s\"" % (act,pvt_act)))

        
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
        logger.debug('Notice Received : ' + user + ' ' + channel + ' ' + message)
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
            mch = re.search("(\w+)\W+is part of this Network's Services", message)
            if mch:
                user = mch.group(1)
                self.nicks_db.set_bot_status(user)
            if re.search('Last seen\s+: now', message, re.I):  
                if self.expecting_nickserv:
                    self.nicks_db.set_nickserv_response(self.expecting_nickserv, 
                                                        approved=True) 
                    self.expecting_nickserv = None
#                    print self.nicks_db.nicks_in_room
#                    print self.nicks_db.nicks_info                                
        if self.plugins:
            self.plugins.noticed(user, channel, message)
#        elif self.factory:
#            self.queue_message(self.factory.channel, 'say', user + ": " + message )

            


    def privmsg(self, user, channel, orig_msg):
        """ This is the ideal place to process commands from the user. """
        logger.debug( "PRIVMSG %s on %s says %s " % ( user, channel, orig_msg))

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



        # if we wish to return a self.msg(...) to an incoming command
        # we need to send it to a nickname if the message was private
        # or to the channel if it was public.  The problem with the 'channel'
        # parameter is that is shows the sender (not the recipient) in the context
        # of a private message.  Hence the need to set the chan variable below.
        if channel == self.factory.nickname:
            chan = user.split('!')[0]
            # determine the trigger for private chat window
            act = get_global_option('pvt-trigger')
            
        else:
            chan = channel.lower()
            # determine the trigger for this room
            act = get_room_option(self.factory.network, channel, 'activation')
        
        if not act: act = '!'

        # set the nick variable for use with self.msg(...) as user,
        # as an argument, doesn't work.  
        nick = user.split('!')[0]
        mch = re.match(re.escape(act)+ "(.*)", msg)
        if mch:
            msg = mch.group(1).strip()
            logger.debug("Received Command " + str((nick, user, chan, orig_msg, msg, act)))
            self.plugins.command(nick, user, chan, orig_msg, msg, act)

        self.plugins.privmsg(user, channel, orig_msg)
    
    def irc_RPL_NAMREPLY(self, prefix, params):
        # We use the RPL_NAMREPLY to get a list of all people currently
        # in a room when the bot first joins that room and uses that information
        # to populate the NicksDB.
        logger.debug("irc_RPL_NAMREPLY "+str(params))
        room = params[2].lower()

        nicks_to_fill_in = []
        names = params[3].strip().split(' ')
#        print names
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
                ident = self.nicks_db.get_host(this_name)
                if ident == None:
                    # need to strip opstatus off first
                    nicks_to_fill_in.append(this_name)
                           
        for ii in range(0, len(nicks_to_fill_in)/5+1):
            nicks_batch = nicks_to_fill_in[ii*5:5*(ii+1)]
            nicks_to_get_hosts = " ".join(nicks_batch)
            self.userhost_in_progress.extend(nicks_batch)
            if nicks_to_get_hosts.strip != "":
                line = "userhost " + nicks_to_get_hosts
#            print line
                self.sendLine(line)        
    
    def irc_RPL_USERHOST(self, prefix, params):
        response = params[1]
        nick_strings = response.strip().split(" ")
        for nick_str in nick_strings:
            nick, host = nick_str.split("=")
            nick = re.sub("\*","", nick)
            host = re.sub("^[~%&@\-\+]+","", host)
            logger.debug("irc_RPL_USERHOST {} = {}".format(nick, host))
            # If the nick is in multiple rooms but it may appear in this list
            # only once so we should be careful
            if nick in self.userhost_in_progress:
                self.userhost_in_progress.remove(nick)
            logger.debug("userhosts in progress = " + str( self.userhost_in_progress))
            self.nicks_db.set_ident(nick, host)
            if self.factory.extra_options['no_services']:
                pass
            else:
                line = 'privmsg nickserv info ' + nick
                self.sendLine(line)            
#        if len(self.userhost_in_progress) == 0:
#            self.say(self.factory.channel, "Nicks DB Initialised")
            
#        print self.nicks_db.nicks_in_room
#        print self.nicks_db.nicks_info
        
    def irc_unknown(self, prefix, command, params):
        """ Used to handle RPL_NAMREPLY and REL_WHOISUSER events
            so that we can keep a track of who is and who isn't
            in channel.  Particularly useful for when the bot
            enters a channel with people already on it."""
        irc.IRCClient.irc_unknown(self, prefix, command, params)

        
        line =  '[server]: ' + prefix + ',' + command + ',' + ','.join(params)
        if command not in ['PONG']: # we don't care about these
            logger.debug(line)
#            self.queue_message(self.factory.channel, 'say', line)



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



class IRCBotFactory(protocol.ClientFactory):
    protocol = IRCBot

    def __init__(self, reactor, server, channel, nickname,  \
                 sys_password, nickserv_pw, web_port, rpc_port, extra_options):
        
        self.shutting_down = False
        self.reactor = reactor
        self.channel = channel
        self.web_port = web_port
        self.rpc_port = rpc_port
        self.nickname = nickname
        self.conn = None  # No IRC connection yet
        self.network = server
        self.nickserv_password = nickserv_pw
        self.sys_password = sys_password
        self.extra_options = extra_options
        
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
        logging.info("Lost connection (%s)", (reason,))
        # Taken from https://twistedmatrix.com/documents/13.1.0/core/howto/time.html
        if not self.shutting_down:
            logging.info("Will reconnect shortly...")
            self.reactor.callLater(3, self.doReconnect, connector)


    def clientConnectionFailed(self, connector, reason):
        logging.info("Could not connect: %s, will reconnect in 10 seconds" % (reason,))
        self.reactor.callLater(10, self.doReconnect, connector)


########################################################################

def instantiateIRCBot(network, port, room, botName, sys_password, 
                      nickserv, web_port = None, rpc_port=None, 
                      extra_options=None):

    
    socket.setdefaulttimeout(30)
    # Start the IRC Bot
    reactor.connectTCP(network, port,
                       IRCBotFactory(reactor, network, room, botName,\
                                     sys_password, nickserv, web_port,\
                                     rpc_port, extra_options))

    
    reactor.run()

def main():
    instantiateIRCBot(IRC_NETWORK, 6667, IRC_ROOM_NAME, BOT_NAME, NICKSERV)

# this only runs if the module was *not* imported
if __name__ == '__main__':
    main()
