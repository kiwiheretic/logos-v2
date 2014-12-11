#! /usr/bin/env python

import psutil # Used to determine available RAM
import sys
import gc
import os
import re
import pdb
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from optparse import OptionParser, make_option

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from django.db.transaction import commit_on_success
from django.db import connection
from django.db.models import Max

from logos.settings import BIBLES_DIR, DATABASES

from logos.models import BibleTranslations, BibleBooks, BibleVerses, \
    BibleConcordance, BibleDict

from _booktbl import book_table
from logos.constants import PUNCTUATION, STOP_WORDS

logger = logging.getLogger(__name__)

class Command(BaseCommand):
#    args = '<poll_id poll_id ...>'
    help = 'Import the translations'

    extra_options = (

#        make_option('--createdb', choices=('translations','strongs',
#                                           'concordance', 'session'),
#                    help="One of 'translations', 'strongs', 'concordance', "+\
#                        "'session'"),
        make_option('--importdb',action='store_true',
                    help="Import translation files and generate concordance"),
        make_option('--repair-if-incomplete', action='store_false', dest='repair',
                    help="Don't ensure the database is empty when using --createdb"),
        make_option('--purge-if-incomplete', action='store_true',dest='purge',
                    help="Check that the translations are complete, if not purge"),

        make_option('--updatedb', action='store_true',
                    help="Update the database"),
        make_option('--search', action='store',
                    help="Test the concordance search function"),
        make_option('--translation', action='store',
                    help="A translation like \"nasb\", \"esv\", \"kjv\", etc."+\
                        " Use with --search"),

    )
    option_list = BaseCommand.option_list + extra_options


    def handle(self, *args, **options):
        logger.debug ("args = "+str(args))
        logger.debug ("options = "+ str(options))

        if DATABASES['bibles']['ENGINE'].endswith('sqlite3'):
            vm = psutil.virtual_memory()
            cursor = connection.cursor()
            cursor.execute("PRAGMA Journal_mode = MEMORY")
            cursor.execute("PRAGMA Page_size")
            row = cursor.fetchone()
            page_size = row[0]
            # use 75% of available VM for cache
            cache_size = int(.75 * vm.available / page_size)
            cursor.execute("PRAGMA Cache_Size = "+str(cache_size))
            print "page_size = " + str(page_size) + " bytes"
            print "cache_size = " + str(cache_size) + " pages"

        import_trans()
        import_concordance()
        # store_true options are None if not used but the keys exist
#        if options['updatedb']:
#            updatedb()

#        elif options['createdb'] == 'concordance':
#            import_concordance()

#        elif options['createdb'] == 'translations':
#            import_trans()
#        elif options['createdb'] == 'strongs':
#            populate_strongs_tables()

#        else:
#            pass

def updatedb(purge=False):
    populate_strongs_tables()
    import_trans(purge=purge)
    import_concordance(purge=purge)

def import_trans(purge=False):
    print "importing translations..."
    print BIBLES_DIR
    valid_books = map(lambda x:x[0], book_table)




    for this_dir in os.listdir(BIBLES_DIR):
        if this_dir[0] != '_' and this_dir != 'dict':
            print this_dir
            biblepath = BIBLES_DIR + os.sep + this_dir
            print biblepath

            for bk in valid_books:
                book_path = biblepath + os.sep + bk
                if os.path.exists(book_path):
                    pass
                elif os.path.exists(book_path + ".txt"):
                    book_path = book_path + ".txt"
                else:
                    print "Could not find book : " + book_path
                    continue
                translation = this_dir
                add_book_to_db(translation, book_path)

def import_concordance(purge=False):
    print "Importing concordance ..."
    populate_concordance(purge=purge)

def populate_concordance(purge=False):
    print "populate concordance"

    for trans in BibleTranslations.objects.all().iterator():

        trans_name = trans.name
        print "Adding missing translation to concordance", trans.name

        conc_cache = []

        if BibleConcordance.objects.exists():
            next_id = BibleConcordance.objects.all().\
                aggregate(Max('id'))['id__max']+1
            last_rec = BibleConcordance.objects.filter(trans_id=trans).last()
            if last_rec:

                lbook = last_rec.book
                lchapter = last_rec.chapter
                lverse = last_rec.verse
                print "continuing from %s %d:%d" % (lbook.long_book_name, lchapter, lverse)
                bv_id = BibleVerses.objects.filter(trans_id=trans, \
                                book = lbook, chapter = lchapter, \
                                verse=lverse).first().id
                bv = BibleVerses.objects.filter(trans_id = trans, pk__gt = bv_id).iterator()  # iterator uses less memory
            else:
                print "No records for this translation yet"
                bv = BibleVerses.objects.filter(trans_id = trans).iterator()



        else:
            next_id = 1
            bv = BibleVerses.objects.filter(trans_id=trans).iterator()  # iterator uses less memory

        idx = 0
        iidx = 0
        for vs in bv:

            text = vs.verse_text
            words = re.split('\s+', text.lower())
            for word_id, wd in enumerate(words):
                wd = re.sub(PUNCTUATION, "", wd)
                if wd == '': continue


                wd_lower = wd.lower()
                assert wd_lower != ''
                if wd_lower not in STOP_WORDS:

                    if BibleConcordance.objects.\
                    filter(trans_id = vs.trans_id,
                           book = vs.book,
                           chapter = vs.chapter,
                           verse = vs.verse,
                           word_id = word_id).exists():
                           pass

                    else:
                        conc = BibleConcordance(id = next_id,
                                                trans_id = vs.trans_id,
                                                book = vs.book,
                                                chapter = vs.chapter,
                                                verse = vs.verse,
                                                word_id = word_id,
                                                word = wd_lower)
                        next_id += 1
                        conc_cache.append(conc)

                    idx+= 1
                    if  idx % 100 == 0:
                        if len(conc_cache) ==0:
                            print "#",
                        else:
                            print ".",
                            BibleConcordance.objects.bulk_create(conc_cache)
                            conc_cache = []
                        iidx += 1
                        if iidx % 35 == 0: print
                        gc.collect()

        BibleConcordance.objects.bulk_create(conc_cache)
        conc_cache = []


@commit_on_success
def add_book_to_db(translation, book_path, purge=False):
    book = os.path.splitext(book_path)[0]
    book = os.path.split(book)[1]

    try:
        new_trans = BibleTranslations.objects.get(name=translation)
    except ObjectDoesNotExist:

        new_trans = BibleTranslations(name = translation)
        new_trans.save()
        print "saved new trans " + translation
        trans_id = new_trans.pk


    long_book, idx = get_long_book_name(book)
    mch = re.match("^([^\.]+)", book)
    if mch:
        base_book = mch.group(1)
    assert base_book

    if not BibleBooks.objects.\
        filter(trans_id = new_trans, canonical = base_book).exists():
        print "adding book ", long_book
        bib_book = BibleBooks(trans_id = new_trans,
                              long_book_name= long_book,
                              book_idx = int(idx),
                              canonical = base_book)
        bib_book.save()

        populate_verses(new_trans, bib_book, book_path)
    else:
        print "%s : %s book already exists - skipping" % (translation, base_book,)

    gc.collect()

def populate_verses(trans_id, book_id, filename):
    """  """
    book_cache = []
    if BibleVerses.objects.exists():
        next_id = BibleVerses.objects.all().\
            aggregate(Max('id'))['id__max']+1
    else:
        next_id = 1

    f = open(filename, "r")
    for lineno, ln in enumerate(f.readlines()):
        if ln.strip() != '':
            mch = re.match('[^\d]*(\d+):(\d+)(\s+|:)(.*)', ln)
            if mch:
                ch = int(mch.group(1))
                vs = int(mch.group(2))
                txt = re.sub('\'', '\'\'', mch.group(4))

                txt = re.sub(r'\\', r'\\\\', txt)
                txt = re.sub('[^\x20-\x7F]', '', txt)
                bv = BibleVerses(id = next_id,
                                 trans_id = trans_id,
                                 book = book_id,
                                 chapter = ch,
                                 verse = vs,
                                 verse_text = txt)
                next_id += 1
                book_cache.append(bv)


            else:
                print "weird -> ", filename, lineno, ln


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

def update_translation(translation, book=None):
    print translation, ":", book

    try:
        trans_id = BibleTranslations.objects.get(name=translation).pk
    except ObjectDoesNotExist:

        new_trans = BibleTranslations(name = translation)
        print "saving new trans " + translation
        new_trans.save()
        print "done"
        trans_id = new_trans.pk

    if book:
        sql_stmt = """select id from bible_books where trans_id = ?
        and abbreviations = ?"""
        c.execute(sql_stmt, (trans_id, book))
        rows = c.fetchone()
        if rows:
            book_id = rows[0]
            print "%s = %s" % (book, book_id)

        else:
            print "Book %s not found" % (book,)
            return
        c2 = db_hash["concordance"].db.cursor()
        sql_stmt = """select count(*) from bible_concordance
        where trans_id = ? and book = ?"""
        c2.execute(sql_stmt, (trans_id, book_id))
        row_cnt = c2.fetchone()[0]
        print "Rows to be deleted in bible_concordance = ", row_cnt

        sql_stmt = """select count(*) from bible_verses
        where trans_id = ? and book = ?"""
        c.execute(sql_stmt, (trans_id, book_id))
        row_cnt = c.fetchone()[0]
        print "Rows to be deleted in bible_verses = ", row_cnt

        sql_stmt = """delete from bible_concordance
        where trans_id = ? and book = ?"""
        c2.execute(sql_stmt, (trans_id, book_id))

        db_hash["concordance"].db.commit()

        sql_stmt = """delete from bible_verses
        where trans_id = ? and book = ?"""
        c.execute(sql_stmt, (trans_id, book_id))
        db_hash["translations"].db.commit()

        pathname = self.bibles + os.sep + translation + os.sep + book
        if not os.path.exists(pathname):
            pathname += ".txt"
        print pathname
        try:
            self._populate_verses(c, trans_id, book_id, pathname)
        except IOError:
            pdb.set_trace()
        db_hash["translations"].db.commit()
        self.populate_concordance(trans_id, book_id)
    else: #translation only
        row_cnt = BibleConcordance.objects.filter(trans_id = trans_id).count()
        print "Rows to be deleted in bible_concordance = ", row_cnt

        row_cnt = BibleVerses.objects.filter(trans_id = trans_id).count()
        print "Rows to be deleted in bible_verses = ", row_cnt

        BibleVerses.objects.filter(trans_id = trans_id).delete()
        BibleConcordance.objects.filter(trans_id = trans_id).delete()

        add_trans_to_db(translation)
        populate_concordance(trans_id)




def get_long_book_name(book):
    idx = 0
    for bk, long_bk in book_table:
        if book == bk:
            return (long_bk, idx)
        idx += 1
    return None
