#!/usr/bin/env python

# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.
from __future__ import absolute_import
from django.core.management.base import BaseCommand, CommandError
import sys
import re

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

        # Named (optional) arguments
        parser.add_argument(
            '--port',
            action='store',
            help='port to receive packets',
        )     

    def handle(self, *args, **options):

        if options['port']:
            port = int(options['port'])
        else:
            port = 5001

        subcommand = options['subcommand']
        if subcommand:
            self.stdout.write('Nothing done')
        else:
            self.stdout.write('Starting symbolics server on port '+str(port))
            self.start_server(port)
            self.stdout.write('Symbolics server terminated')

    def start_server(self, port):
        main(port)

class SymVars:
    """ emptry class for storing variables """
    pass

class SymbolicsServerUDP(DatagramProtocol):
    def __init__(self, *args, **kwargs):
        #super(SymbolicsServerUDP, self).__init__(*args, **kwargs)
        #DatagramProtocol.__init__(self, *args, **kwargs)
        self.nv = MyNodeVisitor()

    def datagramReceived(self, datagram, address):
        cmd = datagram.split(" ")[0]
        arg = re.sub("\S+ ","",datagram,count=1)
        print("cmd {} arg {}".format(cmd, arg))
        if cmd == "hello":
            self.transport.write("hello", address)
        elif cmd == "sym":
            expr = arg
            symvars = SymVars()
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
            datagram = "sym " + datagram
            self.transport.write(datagram, address)

def main(port):
    reactor.listenUDP(port, SymbolicsServerUDP())
    reactor.run()

if __name__ == '__main__':
    main(5001)
