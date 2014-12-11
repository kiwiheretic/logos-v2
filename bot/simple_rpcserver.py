import logging
from logos.settings import LOGGING
logger = logging.getLogger(__name__)
logging.config.dictConfig(LOGGING)
import pickle

from twisted.web import server, resource, xmlrpc
from twisted.internet import reactor
import re
import pdb

class RPC(xmlrpc.XMLRPC):
    def __init__(self, ircfactory):
        xmlrpc.XMLRPC.__init__(self)
        self.ircfactory=ircfactory
        
    def xmlrpc_get_network_name(self):
        if self.ircfactory:
            return self.ircfactory.network

    def xmlrpc_get_nicks_db(self):
        
        if self.ircfactory and self.ircfactory.conn:
            nicks_db = self.ircfactory.conn.nicks_db

            # Can't send objects across twisted RPC, must pickle
            return pickle.dumps(nicks_db)
    
class SimpleRPC():
    def __init__(self, reactor, ircfactory, port):
        rpc = RPC(ircfactory)
        site = server.Site(rpc)
        reactor.listenTCP(port, site)
        
