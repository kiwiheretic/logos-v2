# test plugin
from bot.pluginDespatch import Plugin
import re
import datetime
import logging
from ast1 import MyNodeVisitor, SymVars
import sympy
import ast

from django.conf import settings
logger = logging.getLogger(__name__)
logging.config.dictConfig(settings.LOGGING)

class SympyPlugin(Plugin):
    plugin = ("sym", "Symbolics")
    def __init__(self, *args, **kwargs):
        Plugin.__init__(self, *args, **kwargs)
        
        self.commands = (\
         (r'calc (?P<expr>\S.*)', self.calc, "Performs symbolic computation"),
        )
        self.nv = MyNodeVisitor()
    
    def calc(self, regex, chan, nick, **kwargs):
        expr = regex.group('expr')
        symvars = SymVars()
        try:
            tree = ast.parse(expr)
            self.nv.initvars(var_prefix = "symvars.")
            self.nv.visit(tree)
            #print "result = ",nv.result
            #print "symbols used : " + str(nv.symbol_vars)
            for v in self.nv.symbol_vars:
                if not hasattr(symvars, v):
                    setattr(symvars, v, sympy.symbols(v))
            try:
                result = eval(self.nv.result)
                self.say(chan, str(result))
            except TypeError:
                self.say(chan, "TypeError")
        except SyntaxError, e:
            self.say(chan, "SyntaxError " + e.msg)


    def privmsg(self, user, channel, message):
        pass


            

   
                
            


