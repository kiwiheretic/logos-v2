#! /usr/bin/env python

import psutil # Used to determine available RAM
import sys
import gc
import os
import re
import csv
import json
import codecs
import logging
from datetime import datetime, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db import connection, reset_queries

from django.db.models import Max

from logos.settings import BIBLES_DIR, DATABASES

from bibleapp.models import BibleTranslations, BibleBooks, BibleVerses, \
    BibleConcordance, BibleDict, XRefs

from bibleapp.bot_plugin import BibleBot
from bot.pluginDespatch import PluginDespatcher

from _booktbl import book_table, xref_books
from logos.constants import PUNCTUATION, STOP_WORDS
from logos.utils import *

from django.conf import settings
logger = logging.getLogger(__name__)
logging.config.dictConfig(settings.LOGGING)

class DummyConnection(object):
  def __init__(self):
    class DummyFactory(object):
      def __init__(self):
        self.reactor = None
        self.network = '%shell%'
        self.channel = '%shell%'
    self.factory = DummyFactory()

  def queue_message(self, msgtype, dummychan, msg):
    sys.stdout.write(msg + '\n')

class Command(BaseCommand):
    help = 'Shell to bible bot'

    def add_arguments(self, parser):
      pass

    def handle(self, *args, **options):
        logger.debug ("args = "+str(args))
        logger.debug ("options = "+ str(options))
        irc_conn = DummyConnection()
        self.dispatcher = PluginDespatcher (irc_conn, shell = True )
        self.bot = BibleBot(self, irc_conn)

        try:
          line = raw_input(" % ")
          while line.strip() != "quit":
            sys.stdout.write (line + "\n")
            self.dispatcher.command('%shell%', '%shell%', '%shell%', line, line, '')
            line = raw_input(" % ")
        except EOFError:
          print ("exiting\n")
