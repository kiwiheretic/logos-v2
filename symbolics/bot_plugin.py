# test plugin
from bot.pluginDespatch import Plugin
from twisted.internet.protocol import DatagramProtocol
import re
import datetime
import logging
from ast1 import MyNodeVisitor, SymVars
import sympy
import ast

from django.conf import settings
logger = logging.getLogger(__name__)
logging.config.dictConfig(settings.LOGGING)

class SymbolicsProtocol(DatagramProtocol):
    def __init__(self, conn):
        self.conn = conn

    def startProtocol(self):
        self.transport.connect('127.0.0.1', 5001)
        #self.sendDatagram()
    
    def sendDatagram(self, dgram):
        self.transport.write(dgram)

    def datagramReceived(self, datagram, host):
        print 'Datagram received: ', repr(datagram)
        self.conn.response(datagram)

class SympyPlugin(Plugin):
    plugin = ("sym", "Symbolics")
    def __init__(self, *args, **kwargs):
        super(SympyPlugin, self).__init__(*args, **kwargs)
        
        self.commands = (\
         (r'connect$', self.connect, "Connect to symbolics server"),
         (r'calc (?P<expr>\S.*)', self.calc, "Performs symbolic computation"),
        )
        self.connected = True 

        self.protocol = SymbolicsProtocol(self)
        self.t = self.reactor.listenUDP(0, self.protocol)
        self.q = []

    def connect(self, regex, chan, nick, **kwargs):
        self.protocol.startProtocol()
        self.connected = True
    
    def calc(self, regex, chan, nick, **kwargs):
        expr = regex.group('expr')
        if self.connected:
            self.protocol.sendDatagram(expr)
            self.q.append((chan, expr))
        else:
            self.say(chan, "Not connected to symbolics server")


    def response(self, resp):
        chan, expr = self.q.pop(0)
        self.say(chan, resp)

    def privmsg(self, user, channel, message):
        pass


            

   
                
            


