import logging
from logos.settings import LOGGING
logger = logging.getLogger(__name__)
logging.config.dictConfig(LOGGING)
import pickle

from twisted.web import server, resource, xmlrpc
from twisted.internet import reactor
import re
import types

def proxyobj(obj, max_recursion = 5):
    atomic_types = (types.IntType, types.LongType, types.FloatType, 
        types.StringType, types.UnicodeType)
    if max_recursion == 0: return None
    class Proxy:
        pass
    prxy = None
    if type(obj) == types.DictType:
        d = {}
        for k,v in obj.iteritems():
            if type(v) not in atomic_types:
                vv = proxyobj(v, max_recursion = max_recursion - 1)
            else:
                vv = v
            if vv is not None: d[k] = vv
        return d
    elif type(obj) in (types.TupleType, types.ListType):
        lst = []
        for v in obj:
            if type(v) not in atomic_types:
                vv = proxyobj(v, max_recursion = max_recursion - 1)
            else:
                vv = v
            lst.append(vv)
        return lst
    elif type(obj) == types.InstanceType:
        prxy = Proxy()

        for attr in dir(obj):
            attrval = getattr(obj, attr)
            if type(attrval) not in atomic_types:
                vv = proxyobj(attrval, max_recursion = max_recursion - 1)
            else:
                vv = attrval
                
            if vv is not None: setattr(prxy, attr, vv)
    return prxy       
            
            

class RPC(xmlrpc.XMLRPC):
    def __init__(self, factories, *args, **kwargs ):
        xmlrpc.XMLRPC.__init__(self, *args, **kwargs)
        self.factories=factories
    
    """ method names must be prefixed by xmlrpc_ in order
    for the method to be visible to an RPC client """    
    def xmlrpc_get_networks(self):
        networks = [f.network for f in self.factories]
        return networks

                    
            
        
    def xmlrpc_get_factories(self):
        obj = proxyobj(self.factories, max_recursion = 10)
        return obj
        
    def xmlrpc_get_rooms(self):
        room_list = []
        for f in self.factories:
            if f.conn:
                rooms = f.conn.nicks_db.get_rooms()
                room_data = []
                for room in rooms:
                    ops = f.conn.nicks_db.get_op_status(f.nickname, room)
                    room_data.append({'room':room, 'ops':ops})
                room_list.append({'network':f.network, 'rooms':room_data})
        return room_list


"""
    def xmlrpc_get_network_name(self):
        if self.ircfactory:
            return self.ircfactory.network

    def xmlrpc_get_nicks_db(self):
        
        if self.ircfactory and self.ircfactory.conn:
            nicks_db = self.ircfactory.conn.nicks_db

            # Can't send objects across twisted RPC, must pickle
            return pickle.dumps(nicks_db)
"""
    
class SimpleRPC():
    def __init__(self, reactor, factories, port):
        rpc = RPC(factories, allowNone = True)
        site = server.Site(rpc)
        reactor.listenTCP(port, site)
        
