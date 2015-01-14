#! /usr/bin/env python

import sys
import os
import re
import pdb
import logging
import bot.IRC as irc
from datetime import datetime, timedelta
from decimal import Decimal
from optparse import OptionParser, make_option


from django.core.management.base import BaseCommand, CommandError

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Run the IRC bot'

    extra_options = (

        # I think --db-path is no longer implemented, a relic
        # of logos v1.
        make_option('--db-path', action='store',
        help="""File path to create the settings and user search databases.  """ + \
        "Defaults to APPDATA\\SplatsCreations\\bibleBot for windows " + \
        "and current directory for others."),
        
        make_option('-s','--server', action='store',
                    help="IRC server to connect to."),
        make_option('--port', action='store',
                    help="Server port to connect to.  Defaults to 6667."),
        make_option('--web-port', action='store',
                    help="Web Port to listen on.  Defaults to None."),                    
        make_option('--rpc-port', action='store',
                    help="RPC Port to listen on.  Defaults to None."),                    
        make_option('--engine-room', action='store',
                    help="IRC engine room name to join.  Defaults to #engineroom"),
        make_option('-n', '--nickname', action='store',
                    help="The IRC nickname the bot assumes.  Defaults to MyBible"),
        make_option('--nick-password', '-p', action='store',
                    help="The bot nickserv password.  Defaults to 'qwerty'"),
        make_option('--sys-password', '-P', action='store',
                    help="The bot control password.  Defaults to 'zxcvbnm'"),
        make_option('--no-services', action='store_true',
                    help="Don't try and use IRC services"),
        make_option('--startup-script', action='store',
                    help="path to the startup script of IRC commands"),                    
        make_option('--room-key', action='store',
                    help="The key used to join the control room (if needed)"),

    )
    option_list = BaseCommand.option_list + extra_options

    def handle(self, *args, **options):
#        logger.debug( "options = "+ str(options))

       
        if options['server']:
            server = options['server']
        else:
            server = '127.0.0.1'

        if options['port']:
            port = int(options['port'])
        else:
            port = 6667

        if options['nickname']:
            nickname = options['nickname']
        else:
            nickname = 'bot'

        if options['nick_password']:
            nick_password = options['nick_password']
        else:
            nick_password = ''

        if options['sys_password']:
            sys_password = options['sys_password']
        else:
            sys_password = 'zxcvbnm'
        
        if options['web_port']:
            web_port = int(options['web_port'])
        else:
            web_port = None          

        if options['rpc_port']:
            rpc_port = int(options['rpc_port'])
        else:
            rpc_port = None     
                    
        if options['engine_room']:
            engine_room = options['engine_room']
        else:
            engine_room = '#engineroom'
        
        extra_options = {}
        extra_options['no_services'] = options['no_services']
        extra_options['room_key'] = options['room_key']
        extra_options['startup_script'] = options['startup_script']

        irc.instantiateIRCBot(server, port, engine_room, nickname, \
                              sys_password, nick_password, web_port, rpc_port, \
                              extra_options)

