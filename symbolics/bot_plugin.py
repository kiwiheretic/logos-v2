# test plugin
from bot.pluginDespatch import Plugin
from twisted.internet.protocol import DatagramProtocol
from twisted.internet.error import AlreadyCalled, AlreadyCancelled
import re
import datetime
import logging
from ast1 import MyNodeVisitor, SymVars
import sympy
import ast

from logos.roomlib import get_global_option, set_global_option
from django.conf import settings
logger = logging.getLogger(__name__)
logging.config.dictConfig(settings.LOGGING)

class SymbolicsProtocol(DatagramProtocol):
    def __init__(self, conn):
        self.conn = conn
        self.connected = False

    def connect(self, chan):
        self.chan = chan
        symhost = get_global_option('symbolics-host')
        host, port = symhost.split(':')
        if hasattr(self, "t"): 
            self.t.stopListening()
        self.t = self.conn.reactor.listenUDP(0, self)
        self.transport.connect(host, int(port))
        self.sendDatagram("hello")
        self.pending = self.conn.reactor.callLater(2.0, self.timeout)
        self.cancel = False
    
    def timeout(self):
        if self.cancel:
            print "timeout cancelled"
        else:
            print "timeout"
            self.connected = False
            self.conn.disconnected(self.chan)

    def sendDatagram(self, dgram):
        self.transport.write(dgram)
        self.pending = self.conn.reactor.callLater(2.0, self.timeout)
        self.cancel = False

    def datagramReceived(self, datagram, host):
        print 'Datagram received: ', repr(datagram)
        self.cancel = True
#        try:
#            self.pending.cancel()
#        except (AlreadyCalled, AlreadyCancelled) as e:
#            print e
#            pass
#        else:
        if datagram == "hello":
            self.connected = True
            self.conn.connected(self.chan)
        else:
            self.conn.response(datagram)

class SympyPlugin(Plugin):
    plugin = ("sym", "Symbolics")
    def __init__(self, *args, **kwargs):
        super(SympyPlugin, self).__init__(*args, **kwargs)
        
        self.commands = (\
         (r'connect$', self.connect, "Connect to symbolics server"),
         (r'set host (?P<host>\S+)$', self.set_host, "Set symbolics host"),
         (r'show host$', self.show_host, "Set symbolics host"),
         (r'calc (?P<expr>\S.*)', self.calc, "Performs symbolic computation"),
        )

        symhost = get_global_option('symbolics-host')
        if not symhost:
            set_global_option('symbolics-host', '127.0.0.1:5001')

        self.protocol = SymbolicsProtocol(self)
        self.q = []

    def set_host(self, regex, chan, nick, **kwargs):
        symhost = regex.group('host')
        if re.match(r"\d+", symhost):
            set_global_option('symbolics-host', '127.0.0.1:'+symhost)
            self.say(chan, "Symbolics host set to "+ symhost)
        elif re.match(r"(\d+\.){3}\d+:\d+", symhost):
            set_global_option('symbolics-host', symhost)
            self.say(chan, "Symbolics host set to "+ symhost)
        else:
            self.say(chan, "Symbolics host, invalid format")

    def show_host(self, regex, chan, nick, **kwargs):
        symhost = get_global_option('symbolics-host')
        self.say(chan, "Symbolics host "+ symhost)

    def connect(self, regex, chan, nick, **kwargs):
        self.protocol.connect(chan)

    def connected(self, chan):
        self.say(chan, "Connected to Symbolics Server")

    def disconnected(self, chan):
        self.say(chan, "Disconnected from symbolics server")

    def calc(self, regex, chan, nick, **kwargs):
        expr = regex.group('expr')
        # transport seems to be null if no connection
        if self.protocol.transport:
            self.protocol.sendDatagram("sym "+expr)
            self.q.append((chan, expr))
        else:
            self.say(chan, "Not connected to symbolics server")


    def response(self, resp):
        chan, expr = self.q.pop(0)
        cmd = resp.split(" ")[0]
        msg = re.sub(r"\S+ ", "", resp, count=1)
        print ((cmd, msg))
        self.say(chan, msg)

    def privmsg(self, user, channel, message):
        pass


            

   
                
            


