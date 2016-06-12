#!/usr/bin/env python

# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.
from __future__ import absolute_import
from django.core.management.base import BaseCommand, CommandError
import sys

from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor

import logging
from ...ast1 import MyNodeVisitor, SymVars
import sympy
import ast

from django.conf import settings
logger = logging.getLogger(__name__)
logging.config.dictConfig(settings.LOGGING)

class Command(BaseCommand):
    help = 'Start symbolics server'

    def add_arguments(self, parser):
        parser.add_argument('subcommand', nargs='?')
        

    def handle(self, *args, **options):
        subcommand = options['subcommand']
        if subcommand:
            self.stdout.write('Nothing done')
        else:
            self.stdout.write('Starting symbolics server')
            self.start_server()
            self.stdout.write('Symbolics server terminated')

    def start_server(self):
        main()

class SymVars:
    """ emptry class for storing variables """
    pass

class SymbolicsServerUDP(DatagramProtocol):
    def __init__(self, *args, **kwargs):
        #super(SymbolicsServerUDP, self).__init__(*args, **kwargs)
        #DatagramProtocol.__init__(self, *args, **kwargs)
        self.nv = MyNodeVisitor()

    def datagramReceived(self, datagram, address):
        print("dg "+ datagram)
        symvars = SymVars()
        expr = datagram
        try:
            tree = ast.parse(expr)
            self.nv.initvars(var_prefix = "symvars.")
            self.nv.visit(tree)
            print "result = ",self.nv.result
            print "symbols used : " + str(self.nv.symbol_vars)
            for v in self.nv.symbol_vars:
                if not hasattr(symvars, v):
                    setattr(symvars, v, sympy.symbols(v))
            try:
                result = eval(self.nv.result)
                datagram = str(result)
            except TypeError:
                datagram = "TypeError"
        except SyntaxError, e:
            datagram = "SyntaxError"
        self.transport.write(datagram, address)

def main():
    reactor.listenUDP(5001, SymbolicsServerUDP())
    reactor.run()

if __name__ == '__main__':
    main()
