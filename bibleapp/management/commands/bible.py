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

from _booktbl import book_table, xref_books
from logos.constants import PUNCTUATION, STOP_WORDS
from logos.utils import *

from django.conf import settings
logger = logging.getLogger(__name__)
logging.config.dictConfig(settings.LOGGING)

class Command(BaseCommand):
    help = 'Import the translations'

    def add_arguments(self, parser):

        # Named (optional) arguments
        parser.add_argument('--xrefs',
            action='store_true',
            default=False,
            help="Import cross-references.txt file into database")

        parser.add_argument('--remove-translation',
            action='store',
            help="Purge translation from database")

        parser.add_argument('--replace-version',
            action='store',
            help="Only replace the specified translation in the" + \
            "database.  Should be a folder name in bibles/")

        parser.add_argument('--use-more-ram',
            action='store_true',
            default=False,
            help="Try to speed up a sqlite3 database import by " + \
                "storing the journal in ram")

        parser.add_argument('--import',
            action='store_true',
            default=False,
            help="Import the database to original plain text files")

        parser.add_argument('--export',
            action='store_true',
            default=False,
            help="Export the database to original plain text files")

    def handle(self, *args, **options):
        logger.debug ("args = "+str(args))
        logger.debug ("options = "+ str(options))

        if options['xrefs']:
            import_xrefs()
            return

        if options['export']:
            dump_db()
            return

        if 'remove_translation' in options:
            trans = options['remove_translation']
            result = purge_translation(trans)
            if result == False:
                print "Could not find translation {}".format(trans)
            else:
                print "Translation {} removed from database".format(trans)
            return

        if options['use_more_ram'] and DATABASES['bibles']['ENGINE'].endswith('sqlite3'):
            logger.info("Allocating the SQLITE3 journal in RAM")
            vm = psutil.virtual_memory()
            cursor = connection.cursor()
            cursor.execute("PRAGMA Journal_mode = MEMORY")
            cursor.execute("PRAGMA Page_size")
            row = cursor.fetchone()
            page_size = row[0]
            # use 75% of available memory for cache
            cache_size = int(.75 * vm.available / page_size)
            cursor.execute("PRAGMA Cache_Size = "+str(cache_size))
            print "page_size = " + str(page_size) + " bytes"
            print "cache_size = " + str(cache_size) + " pages"

        

        if options['import'] or options['replace_version']:
            if options['replace_version']:
                version = options['replace_version']
                biblepath = BIBLES_DIR + os.sep + version        
                if not os.path.exists(biblepath):
                    print "Version %s does not exists in bibles/" % (version,)
                    return
            else:
                # don't bother repopulating the strongs tables if we are just
                # replacing a single translation
                try:
                    import_strongs_tables() 
                except IOError:
                    # If dict folder doesn't exist then just carry on
                    pass
            import_trans(options)
            import_concordance(options)
        else:
            print "Nothing to do"

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

def import_xrefs():
    file_path = os.path.join(BIBLES_DIR, 'dict', 'cross_references.txt')
    f = open(file_path, 'r')
    XRefs.objects.all().delete()
    cache = []
    idx = 0
    for ln in f.readlines():
        try:
            entry1, entry2, votes = ln.strip().split('\t')
        except ValueError:
            continue
        
        prim_book, prim_ch, prim_vs = entry1.split('.')
        if '-' in entry2:
            entry2a, entry2b = entry2.split('-')
            xref_book, xref_ch, xref_vs = entry2a.split('.')
            xref_book2, xref_ch2, xref_vs2 = entry2b.split('.')
        else:
            xref_book, xref_ch, xref_vs = entry2.split('.')
            xref_book2, xref_ch2, xref_vs2 = (None, None, None)
        
        xrefs = XRefs(primary_book = book_table[xref_books.index(prim_book)][0],
                primary_chapter = prim_ch,
                primary_verse = prim_vs,
                xref_book1 = book_table[xref_books.index(xref_book)][0],
                xref_chapter1 = xref_ch,
                xref_verse1 = xref_vs,
                xref_book2 = book_table[xref_books.index(xref_book2)][0] if xref_book2 is not None else None,
                xref_chapter2 = xref_ch2,
                xref_verse2 = xref_vs2,
                votes = votes)
        cache.append(xrefs)
        idx += 1
        if idx % 500 == 0:
            XRefs.objects.bulk_create(cache)
            cache = []
            # xrefs.save()
            print ".",

    XRefs.objects.bulk_create(cache)
    
def import_strongs_tables():

    cache = []
    idx = 0

    #BibleDict.objects.all().delete()
    for lang,prefix in (('grk', 'G'), ('heb', 'H')):
        print lang, prefix
        file1 = os.path.join(BIBLES_DIR, 'dict', lang)
        f = open(file1, 'rb')
        for line in f.readlines():
            
            mch = re.match('(\d+)\s+(.*)', line)
            if mch:
                num = prefix+str(mch.group(1))
                text = mch.group(2).decode("utf8", "replace")
                try:
                    dict_obj = BibleDict.objects.get(strongs=num)
                except BibleDict.DoesNotExist:
                    dict_obj = BibleDict(id=idx+1, strongs=num, description=text)
                    if len(cache) > 0 and dict_obj.strongs == cache[-1].strongs:
                        pdb.set_trace()
                    cache.append(dict_obj)
                idx += 1
            else:
                print "strange dict line : " + line

            # This horrible kludge is because the bulk_create
            # method fails somewhere in the middle when inserting
            # large numbers of records (but does not fail when inserting
            # them individually) so I temporarily reduce the number of 
            # objects to insert and then increase it again.  Does this only happen
            # when using Sqlite3 as a database? Is this a known bug in Django?
            if idx > 6000:
                modulus = 100
            elif idx > 5620:
                modulus = 1
            elif idx > 5600:
                modulus = 10
            else:
                modulus = 200
                
            ### End Kludge ###
            
            if  idx % modulus == 0:
                if len(cache) ==0:
                    print "#",
                else:
                    print "(%d, %s) " % (idx,cache[-1].strongs),
                    BibleDict.objects.bulk_create(cache)
                    cache = []
                    gc.collect()
              
            
        f.close()
        BibleDict.objects.bulk_create(cache)

def import_trans(options):
    print "importing translations..."
    print BIBLES_DIR
    valid_books = map(lambda x:x[0], book_table)

    def process_books(version):
        biblepath = BIBLES_DIR + os.sep + version
        trans_file = biblepath + os.sep + "trans_file.csv"
        map_file = biblepath + os.sep + "mappings.json"
#        print biblepath
        for bk in valid_books:
            book_path = biblepath + os.sep + bk
            if os.path.exists(book_path):
                pass
            elif os.path.exists(book_path + ".txt"):
                book_path = book_path + ".txt"
            else:
                print "Could not find book : " + book_path
                continue
            translation = version
            add_book_to_db(translation, book_path)


        # process apocraphyl books in folder (if any).
        # Uses the csv file in the same folder to determine what are
        # the apocraphyl files.
        
        if os.path.exists(map_file):
            with open(map_file, 'rb') as mapfile:
                map_data = json.load(mapfile)
                for filename in map_data['files'].keys():
                    book_path = biblepath + os.sep + filename + ".txt"
                    long_name = map_data['files'][filename]['humanised']
                    shortcut = map_data['files'][filename]['shortcut']
                    if os.path.exists(book_path):
                        logger.info("Adding apocraphyl book " + long_name)
                        add_book_to_db(translation, book_path, 
                                       long_name=long_name,
                                       cononical=shortcut)
                    else:
                        logger.error( "Error in adding apocraphyl book %s %s" %(version, long_name))

        elif os.path.exists(trans_file):
            with open(trans_file, 'rb') as csvfile:
                csvreader = csv.reader(csvfile)
                for row in csvreader:
                    long_name = row[0]
                    short_name = row[1].strip()
                    book_path = biblepath + os.sep + short_name + ".txt"
                    if os.path.exists(book_path):
                        add_book_to_db(translation, book_path, long_name=long_name)
                    else:
                        logger.error( "Error: Apocraphyl book path {} does not exist".format(book_path))
          
    if options['replace_version']:
        version = options['replace_version']
        print "Purging translation " + version
        purge_translation(version)
        process_books(version)
    else:
        for this_dir in os.listdir(BIBLES_DIR):
            if this_dir[0] != '_' and this_dir != 'dict':
                biblepath = BIBLES_DIR + os.sep + this_dir
                print biblepath
                process_books(this_dir)

            
def import_concordance(options):
    print "Importing concordance ..."
    if options['replace_version']:
        version = options['replace_version']
        purge_concordance(version)
    populate_concordance(options)

def purge_concordance(version):
    print "Purging concordance of " + version
    try:
        trans = BibleTranslations.objects.get(name=version)
    except ObjectDoesNotExist:
        return
    BibleConcordance.objects.filter(trans=trans)      

def populate_concordance(options):
    """ Run through the bible verse database looking up all verses
    and create concordance records for each word (except common words)"""


    def really_pop_concordance(version):
        conc_cache = []
        try:
            trans = BibleTranslations.objects.get(name=version)
        except ObjectDoesNotExist:
            return
        if BibleConcordance.objects.exists():
            next_id = BibleConcordance.objects.all().\
                aggregate(Max('id'))['id__max']+1
            last_rec = BibleConcordance.objects.filter(trans=trans).last()
            if last_rec:

                lbook = last_rec.book
                lchapter = last_rec.chapter
                lverse = last_rec.verse
                logger.info( "continuing from %s %d:%d" % \
                            (lbook.long_book_name, lchapter, lverse))
                bv_id = BibleVerses.objects.filter(trans=trans, \
                                book = lbook, chapter = lchapter, \
                                verse=lverse).first().id
                bv = BibleVerses.objects.filter(trans = trans, pk__gt = bv_id).iterator()  # iterator uses less memory
            else:
                print "No records for this translation yet"
                bv = BibleVerses.objects.filter(trans = trans).iterator()



        else:
            next_id = 1
            bv = BibleVerses.objects.filter(trans=trans).iterator()  # iterator uses less memory

        idx = 0
        iidx = 0
        for vs in bv:
            text = re.sub(r"-", " ",  vs.verse_text)
            text = re.sub(r"[^a-zA-Z0-9\s]", "",  text)
#            text = re.sub(PUNCTUATION, "", text)
            if not text:
                continue
            words = re.split('\s+', text.lower().strip())
            for word_id, wd in enumerate(words):
#                wd = re.sub(PUNCTUATION, "",) wd)
                try:
                    assert wd != ""
                except AssertionError:
                    logger.error("line was {}".format(vs.verse_text))
                    logger.error("words is " + str(words))
                    continue
#                if wd == '': continue


                wd_lower = wd.lower()
                assert wd_lower != ''
                if wd_lower not in STOP_WORDS:

                    if BibleConcordance.objects.\
                    filter(trans = vs.trans,
                           book = vs.book,
                           chapter = vs.chapter,
                           verse = vs.verse,
                           word_id = word_id).exists():
                           pass

                    else:
                        conc = BibleConcordance(id = next_id,
                                                trans = vs.trans,
                                                book = vs.book,
                                                chapter = vs.chapter,
                                                verse = vs.verse,
                                                word_id = word_id,
                                                word = wd_lower)
                        next_id += 1
                        conc_cache.append(conc)

                    idx+= 1
                    if  idx % 500 == 0:
                        if len(conc_cache) ==0:
                            print "#",
                        else:
                            print ".",
                            BibleConcordance.objects.bulk_create(conc_cache)
                            conc_cache = []
                        iidx += 1
                        if iidx % 35 == 0: print
                        gc.collect()

                        # reset_queries, workaround for large databases
                        # See http://travelingfrontiers.wordpress.com/2010/06/26/django-memory-error-how-to-work-with-large-databases/
                        # and https://docs.djangoproject.com/en/dev/faq/models/#why-is-django-leaking-memory
                        reset_queries()

        BibleConcordance.objects.bulk_create(conc_cache)
        conc_cache = []

        
    
    if options['replace_version']:
        version = options['replace_version']
        print "populate concordance with " + version
        really_pop_concordance(version)
    else:    
        for trans in BibleTranslations.objects.all().iterator():
        
            trans_name = trans.name
            print "Adding missing translation to concordance", trans.name

            really_pop_concordance(trans.name)



@transaction.atomic
def purge_translation(translation):
    """ Delete entire translation/version from database """
    try:
        trans = BibleTranslations.objects.get(name=translation)
    except ObjectDoesNotExist:
        return False
    BibleVerses.objects.filter(trans = trans).delete()
    BibleBooks.objects.filter(trans = trans).delete()
    trans.delete()
    return True


@transaction.atomic
def add_book_to_db(translation, book_path, long_name = None, cononical=None):
    book = os.path.splitext(book_path)[0]
    book = os.path.split(book)[1]

    try:
        new_trans = BibleTranslations.objects.get(name=translation)
    except ObjectDoesNotExist:

        new_trans = BibleTranslations(name = translation)
        new_trans.save()
        logger.info( "Generating new translation: " + translation)
        trans = new_trans.pk

    if long_name:
        max_bb = BibleBooks.objects.filter(trans = new_trans).aggregate(Max('book_idx'))
        idx = max_bb['book_idx__max']+1
        long_book = long_name
    else:
        long_book, idx = get_long_book_name(book)
    if not cononical:
        mch = re.match("^([^\.]+)", book)
        if mch:
            cononical = mch.group(1)
    assert cononical

    if not BibleBooks.objects.\
        filter(trans = new_trans, canonical = cononical).exists():
        print "adding book ", long_book
        bib_book = BibleBooks(trans = new_trans,
                              long_book_name= long_book,
                              book_idx = int(idx),
                              canonical = cononical)
        bib_book.save()

        populate_verses(new_trans, bib_book, book_path)
    else:
        print "%s : %s book already exists - skipping" % (translation, cononical,)

    gc.collect()

def populate_verses(trans, book_id, filename):
    """ Add a book (of the bible) file in CancelBot 
    format to the database """
    book_cache = []
    if BibleVerses.objects.exists():
        next_id = BibleVerses.objects.all().\
            aggregate(Max('id'))['id__max']+1
    else:
        next_id = 1

    for cdc in ('cp1253', 'utf-8'):
        try:
            f = codecs.open(filename, 'rb', cdc)
            lines = list(f.readlines())
        except UnicodeDecodeError:
            pass
        else:
            break
    for lineno, ln in enumerate(lines):
        if ln.strip() != '':
            mch = re.match('[^\d]*(\d+):(\d+)(\s+|:)(.*)', ln)
            if mch:
                ch = int(mch.group(1))
                vs = int(mch.group(2))
                # bug?  causes double quotes in output
                #txt = re.sub('\'', '\'\'', mch.group(4))

                #txt = re.sub(r'\\', r'\\\\', txt)
                
#                if re.search(r"rev\.txt", filename) and ch==2 and vs ==3:
#                    pdb.set_trace()
                txt = mch.group(4).encode("utf-8", "replace_spc")
                bv = BibleVerses(id = next_id,
                                 trans = trans,
                                 book = book_id,
                                 chapter = ch,
                                 verse = vs,
                                 verse_text = txt)
                next_id += 1
                book_cache.append(bv)


            else:
                try:
                    weird_line =  u"weird -> {} {} {}".format(filename, lineno, ln)
                    print weird_line.encode("ascii", "replace_spc")
                except UnicodeDecodeError:
                    pdb.set_trace()

    BibleVerses.objects.bulk_create(book_cache)

def populate_strongs_tables():

    BibleDict.objects.all().delete()
    file1 = os.path.join(BIBLES_DIR, 'dict', 'grk')
    f = open(file1, 'rb')
    for line in f.readlines():

        mch = re.match('(\d+)\s+(.*)', line)
        if mch:
            num = "G"+str(mch.group(1))
            text = mch.group(2) #.encode("utf8", "replace")
            # fix unicode errors
            text = re.sub('[\x80-\xFF]', '', str(text))
            dict = BibleDict(strongs = num, description = text)
            dict.save()
    f.close()

    file1 = os.path.join(BIBLES_DIR, 'dict', 'heb')
    f = open(file1, 'rb')
    for line in f.readlines():
        mch = re.match('(\d+)\s+(.*)', line)
        if mch:
            num = "H"+str(mch.group(1))
            text = str(mch.group(2)) #.decode("utf8", "replace")
            # fix unicode errors
            text = re.sub('[\x80-\xFF]', '', str(text))
            dict = BibleDict(strongs = num, description = text)
            dict.save()


    f.close()


def get_long_book_name(book):
    idx = 0
    for bk, long_bk in book_table:
        if book == bk:
            return (long_bk, idx)
        idx += 1
    return None
