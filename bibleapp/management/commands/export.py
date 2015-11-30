#! /usr/bin/env python

import sys
import os
import re
import codecs
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from optparse import OptionParser, make_option

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

from django.db.models import Max

from django.conf import settings # BIBLES_DIR, DATABASES

from bibleapp.models import BibleTranslations, BibleBooks, BibleVerses, \
    BibleConcordance, BibleDict

from _booktbl import book_table
from logos.constants import PUNCTUATION, STOP_WORDS
from logos.utils import *

from django.conf import settings
logger = logging.getLogger(__name__)
logging.config.dictConfig(settings.LOGGING)

class Command(BaseCommand):
    help = 'Import the translations'

    extra_options = (

        make_option('--dump',action='store_true',
                    help="Dump bible database to bibles/ folder (Does not overwrite)"),
    )
    option_list = BaseCommand.option_list + extra_options


    def handle(self, *args, **options):
        logger.debug ("args = "+str(args))
        logger.debug ("options = "+ str(options))
        
        if options['dump']:
            dump_db()
                  

def dump_db():
    biblepath = settings.BIBLES_DIR 
    for trans in BibleTranslations.objects.all():
        vers_path = os.path.join(biblepath, trans.name)
            
        if not os.path.exists(vers_path):
            print vers_path
            os.mkdir(vers_path)
            for bk in trans.biblebooks_set.order_by('id'):
                filepath = os.path.join(vers_path, bk.canonical+".txt")
                f = codecs.open(filepath, 'wb', 'utf-8')
                for vs in bk.bibleverses_set.order_by('chapter','verse'):
                    f.write(u"{}:{} {}\n".format(vs.chapter, vs.verse, vs.verse_text))
                
                f.close()
        else:
            print "skipping " + trans.name + " (already exists)"