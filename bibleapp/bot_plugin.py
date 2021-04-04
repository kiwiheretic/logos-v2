#  BibleBot
from __future__ import absolute_import

# Whether to use threads for concordance searches or not.
# (This is an experimental feature.)

from django.conf import settings

if settings.IM_IN_TEST_MODE:
    THREADED_SEARCH = False
else:
    THREADED_SEARCH = True


import datetime
import re
import asyncio
import time
import copy
from itertools import islice

from logos.constants import PUNCTUATION, STOP_WORDS
from logos.utils import replace_spc_error_handler

from bot.logos_decorators import irc_room_permission_required, \
    irc_network_permission_required
    
from twisted.internet.error import AlreadyCalled, AlreadyCancelled
from django.db.models import Min, Max

from bot.pluginDespatch import Plugin, CommandException
from logos.roomlib import get_room_option, set_room_option, set_global_option, \
    get_global_option, get_user_option
from logos.pluginlib import CommandDecodeException
from .models import BibleTranslations, BibleBooks, BibleVerses, \
    BibleConcordance, BibleDict, XRefs
from .models import BibleColours

from bibleapp.management.commands._booktbl import book_table

import logging
from logos.settings import LOGGING
from django.db.models import Count

logger = logging.getLogger(__name__)
logging.config.dictConfig(LOGGING)

# from http://stackoverflow.com/questions/3313590/check-for-presence-of-a-sublist-in-python
def contains_sublist(lst, sublst):
    n = len(sublst)
    return any((sublst == lst[i:i+n]) for i in xrange(len(lst)-n+1))

# Strip out unneeded punctuation (and other fluff) from a list of words    
def strip_fluff_to_list(text):
    words = []
    for w in re.split('\s+', text):
        w1 = re.sub("[^a-zA-Z0-9'*]", "", w)
        if not re.match("[a-zA-Z0-9']+\*?", w1):
            continue
        else:
            words.append(w1)
    return words

    
def get_book(version, bookwork):
    
    # remove possible spaces between books like "1 John" etc
    book = re.sub("\s+", "", bookwork)
    
    bl = len(book)
    
    book_found = None
    for smallbk, bigbk1 in book_table:
        bigbk = re.sub("\s+", "", bigbk1).lower()
        if smallbk == book:
            book_found = smallbk
            break
        if bigbk[0:bl] == book:
            book_found = smallbk
            break
    
    if not book_found:
        trans = BibleTranslations.objects.get(name=version)
        if BibleBooks.objects.filter(trans=trans, canonical = book).exists():
            return book
        else:
            return None
    
    return book_found

        
class BibleBot(Plugin):

    # stop words are words that are so common that they
    # are not indexed (in the concordance).  It makes for a lot
    # smaller concordance database.
    stop_words = STOP_WORDS
    plugin = ("bible", "Bible Bot")
    
    def __init__(self, *args, **kwargs):
        super(BibleBot, self).__init__(*args, **kwargs)
        
        self.commands = (\
                         (r'random$', self.random_verse, "bring up random verse"),
                         (r'random (?P<translation>[a-zA-Z]+)$', self.random_verse, "bring up random verse"),
                         (r'view$', self.view_xrefs, "View the next xref"),
                         (r'(next|n)\s*$', self.next, "read next verse"),
                         (r'(?:search|s)\s+((?:\w+\s+)?(?:\w+(?:-\w+)?\s+)?[^"]+)$', self.search, "perform a concordance search"),
                         (r'(?:search|s)\s+((?:\w+\s+)?(?:\w+(?:-\w+)?\s+)?)\"([^"]+)\"\s*$', self.phrase_search, "perform a phrase search"),
#                         (r'(?:search|s)\s+([^"]+)', self.search, False),
                         (r'(?:search|s)\s*$', self.next_search, "continue a search"),
                         (r'set\s+(?P<room>#\S+)\s+default\s+translation\s+([a-zA-Z]+)', self.set_default_trans,\
                          "set default translation for room"),
                         (r'set\s+(?:private|pvt)\s+translation\s+([a-zA-Z]+)', self.set_pvt_translation,
                          "set default translation for private chat window"),
                         (r'set\s+(?P<room>#\S+)\s+search\s+limit\s+(\d+)\s*$', self.set_search_limit,
                          "set limit on number of verses searched at once"),
                         (r'set\s+(?P<room>#\S+)\s+verse\s+limit\s+(\d+)\s*$', self.set_verse_limit,
                          "set limit on number of verses read at once"),
                         (r'(?:translations|versions)\s*$', self.versions, 
                          "display available versions or translations"),
                         (r'dict\s+(\S+)', self.dict, "lookup strongs numbers"),
                         (r'(\w+\+?\s+)?\d?\s*[a-zA-Z]+\s+\d+\s*(:?\s*\d+\s*(-?\s*\d+)?)?$',
                          self.verse_lookup, "lookup bible verse", "LastResortMatch"), \
                         (r'books\s+(.*)',
                          self.book_names, "show book names for translation"),
                         (r'xref\s+(.*)',
                          self.xref, "display xref verses"),
                         )

        
        # pending_searches used to remember
        # where up to with users searches
        # so that when they type !next it
        # follows on logically
        self.pending_searches = {}
        
        self.reading_progress = {}

        self.xref_views = {}
    
    def _get_translations(self):
        trans = BibleTranslations.objects.all()    
        trans_list = []
        for tr in trans:
            trans_list.append(tr.name)
        return trans_list
    
    def _get_defaulttranslation(self, channel, nick):
        return "kjv"

    def _get_verselimit(self,channel):
        """ Get maximum number of verses that may be shown in room at one
        bot command """
        return 4

#        res = get_room_option(self.network, channel, "verselimit")
#
#        if not res:
#            res = 4 # default verselimit
#        return res

    def _get_searchlimit(self, channel):
        """ Get the maximum numbers of verses to be shown while
        doing a search in this room """
        return 5
#        res = get_room_option(self.network, channel, "searchlimit")
#        if not res:
#            res = 5 # default search limit setting
#        return int(res)
#
    def _get_verses(self, chan, nick, user, passage_ref):
        """ Retrieve the passage using the passage lookup supplied.
        This will look something like 'nasb john 3:3-5'
        """
        
        # Get the maximum number of verses to display in one
        # go for the current room
        verselimit = int(self._get_verselimit(chan))

        # Find default translation for the current room
        def_trans = self._get_defaulttranslation(chan, nick)

        passage_ref = passage_ref.lower().strip()
        mch1 = re.match(r"([a-z\+]+)\s+([1-3]?\s*[a-z]+)\s+(.*)", passage_ref)
        mch2 = re.match(r"([1-3]?\s*[a-z]+)\s+(.*)", passage_ref)
        if mch1:
            mch = mch1
        elif mch2:
            mch = mch2
        else:
            raise CommandException(nick, chan, \
                        "Could not decipher scripture lookup " +\
                        "reference.  Format is " +\
                        "[translation] <book> <chapter>:<verse>[-<verse>]")

        assert mch.lastindex in (2,3)

        if mch.lastindex == 2:  # No version/translation given
            version = def_trans
            bookwork = mch.group(1)
            versework = mch.group(2)
        if mch.lastindex == 3: # all three given version/book/chapter&verse
            version = mch.group(1)
            bookwork = mch.group(2)
            versework = mch.group(3)
        try:
            trans = BibleTranslations.objects.get(name = version).pk
        except BibleTranslations.DoesNotExist:
            raise CommandException(nick, user, "Unknown translation %s" % (version,))

        # remove possible spaces between books like "1 John" etc
        book = get_book(version, bookwork)
        if not book:
            raise CommandException(user, chan, "Could not find book %s" % (bookwork,))


        passage = re.sub(r"(\d+)\s*:\s*(\d+)",r"\1:\2",versework)

        splitwork = re.split('(?::|-|\s+)',passage)

        chapter = int(splitwork.pop(0))
        if splitwork:
            firstverse = int(splitwork.pop(0))
            if splitwork:
                lastverse = int(splitwork.pop(0))
            else:
                lastverse = firstverse

            if lastverse - firstverse <= verselimit-1 and lastverse > firstverse:
                versecount = lastverse - firstverse + 1
            elif lastverse <= firstverse:
                versecount = 1
            else:
                versecount = verselimit
        else:
            firstverse = 1
            versecount = verselimit


             

        book_db = BibleBooks.objects.get(trans = trans,
                                         canonical = book)
        book_id = book_db.pk
        long_book_name = book_db.long_book_name
        

        # get qualifying verses
        qual_verses = BibleVerses.objects.filter(trans = trans,
                                   book = book_id,
                                   chapter = int(chapter),
                                   verse__gte = firstverse,
                                   verse__lt = firstverse+versecount)

        if qual_verses:
            for v in qual_verses:
                pk = v.pk
            qual_verses_next_pk = pk + 1

            resp = []
            for q in qual_verses:
                resp.append((version.upper(),
                            long_book_name + " " + str(q.chapter) \
                                + ":" + str(q.verse),
                            q.verse_text))
            timestamp = datetime.datetime.now()
            if nick.lower() not in self.reading_progress:
                self.reading_progress[nick.lower()] = {}
            self.reading_progress[nick.lower()][chan.lower()] = \
                {'verses_pk':qual_verses_next_pk,
                 'timestamp': timestamp}
        else:
            raise CommandException(nick, user, \
                "Verse {} {}:{} not found".format(long_book_name, chapter, firstverse))
        return resp
    
    def _next_reading(self, chan, user):
        if user.lower() not in self.reading_progress or \
        chan.lower() not in self.reading_progress[user.lower()]:
            self.say(chan, "No previous verse to read from")
            return None
        else:
            verses_pk = self.reading_progress[user.lower()][chan.lower()]['verses_pk']
            qual_verses = BibleVerses.objects.filter(pk__gte = verses_pk)
        
        # Get the maximum number of verses to display in one
        # go for the current room
        verselimit = self._get_verselimit(chan)
        
        resp = []
        qual_verses_next_pk = None
        for q in qual_verses[0:verselimit]:
            resp.append((q.trans.name.upper(),
                        q.book.long_book_name + " " + str(q.chapter) \
                            + ":" + str(q.verse),
                        q.verse_text))
            qual_verses_next_pk = q.pk + 1
        
        timestamp = datetime.datetime.now()

        if qual_verses_next_pk:
            if user.lower() not in self.reading_progress:
                self.reading_progress[user.lower()] = {}
            self.reading_progress[user.lower()][chan.lower()] = \
                {'verses_pk':qual_verses_next_pk,
                 'timestamp': timestamp}
        else:
            if chan.lower() in self.reading_progress[user.lower()]:
                del self.reading_progress[user.lower()][chan.lower()]
        return resp
    
    def _concordance_generator(self, chan, nick, trans, book_range, words, mode="simple"):

        sri = 1  # This is the search result index
        
        if book_range[0]:
            bk = get_book(trans.name, book_range[0])
            br0 = BibleBooks.objects.filter(trans = trans, canonical=bk)\
                .first()
        else:
            br0 = None
        if book_range[1]:
            bk = get_book(trans.name, book_range[1])
            br1 = BibleBooks.objects.filter(trans = trans, canonical=bk)\
                .first()
        else:
            br1 = None
             
        for w in words:
            if w == "*":
                raise CommandException(nick, chan, \
                            "Bare wildcards cannot be used in search")
                                
        # strip out punctuation from word list 
        word_list = strip_fluff_to_list(' '.join(words))

        # remove commonly occurring stop words from word list
        # (being careful not to iterate over list we are removing from)
        # word_list2 will contain the original list
        stop_words_found = []
        word_list2 = copy.copy(word_list)
        for wrd in word_list2:
            if wrd in self.stop_words:
                # remove from orignal list
                word_list.remove(wrd)
                stop_words_found.append(wrd)
                
        if stop_words_found:
            self.say(chan, "Ignoring common words \"%s\"." % (", ".join(stop_words_found)))
     
        # split word list into those that are wildcards
        # and those that are not.
        normal_words = []
        wild_words = []
        for w in word_list:
            if re.match("([a-zA-Z']+)\*$",w):
                wild_words.append(w)
            else:
                normal_words.append(w)
                        
        logger.debug("normal_words = " + str(normal_words))
        logger.debug("wild_words = " + str(wild_words))
        
        if len(word_list) == 0:
            raise CommandException(nick, chan, \
                        "At least one non stop word needed in search")            
        elif len(word_list) > 1:
            # To save ourselves some work find the word 
            # with the lowest number of occurences in concordance
            lowest = None
            # If there is a book range search only between those books
            # otherwise search the entire translation within the 
            # concordance.
            
            if br0 and br1:
                q_results = BibleConcordance.objects.\
                    filter(trans = trans, book__gte = br0, 
                           book__lte = br1)
            else:
                q_results = BibleConcordance.objects.filter(trans = trans)
            
            if len(normal_words) > 0:
                #s = "word in (" + ", ".join('\'{0}\''.format(re.sub('\'','\'\'', w)) for w in normal_words) +")"
                s = "word in (" + ", ".join('\'{0}\''.format(w) for w in normal_words) +")"
                logger.debug("where clause is \""+s +"\"")
                q0_results = q_results.extra(where=[s])
                q0_results = q0_results.values('word').annotate(Count('word'))
            # Example format of q_results
            # (Pdb) q_results
            # [{'word__count': 988, 'word': u'jesus'}, {'word__count': 80, 'word': u'wept'}]
                               
            # Now do the same for the wildcards.  This turns out to be hard
            # to do because there doesn't seem to be a single query which can
            # annotate all wildcard matches.  So we have to do them one by one.
            match_counts = []
            for w in wild_words:
                q2_results = q_results.all()
                mch = re.match("([a-zA-Z0-9']+)", w)
                w1 = mch.group(1)
                where_str = "word like '%s%%'" % (w1,)
                logger.debug("where_str = " + where_str)
                q2_results = q2_results.extra(where = [where_str])
                counted = q2_results.count()
                match_counts.append({'word__count': counted, 'word': w })
                logger.debug( "Count of %s = %d" % (w, counted))
            
            # Append the two lists together
            if normal_words:
                for q in q0_results:
                    match_counts.append(q)
            
            for q1 in match_counts:
                if lowest == None or q1['word__count'] < lowest:
                    lowest = q1['word__count']
                    wrd = q1['word']
                logger.debug("Lowest word count for %s is %d" % (wrd, lowest))
        else: # only one word in word list
            wrd = word_list[0]
        
        # Find all occurrences of this word with lowest occurrence 
        # frequency
        word_list.remove(wrd)
        
        logger.debug("Query Concordance DB")
        
        # If a book range is defined the find all 
        # concordance lookups in that range
        mch = re.match("([a-zA-Z']+)\*$",wrd)
        if br0 and br1:
            # Is this word a wildcard word?
            if mch:
                w = mch.group(1)
                conc_words = BibleConcordance.objects.\
                    filter(trans = trans, book__gte = br0, book__lte = br1)\
                    .extra(where=["word like '%s%%'" % w])\
                    .order_by('book', 'chapter', 'verse')
            else:
                conc_words = BibleConcordance.objects.\
                    filter(trans = trans, book__gte = br0, book__lte = br1,\
                    word = wrd).order_by('book', 'chapter', 'verse')
        # Otherwise 
        else:
            # Is this word a wildcard word?
            if mch: 
                w = mch.group(1)
                conc_words = BibleConcordance.objects.filter(trans = trans)\
                    .extra(where=["word like '%s%%'" % w])\
                    .order_by('book', 'chapter', 'verse')

            else:           
                conc_words = BibleConcordance.objects.filter(trans = trans,
                    word = wrd).order_by('book', 'chapter', 'verse')
        logger.debug("Number of concordance occurrences of word %s = %d" % (wrd, len(conc_words),))
        
        last_book = None
        last_chapter = None
        last_verse = None

        for wrd_rec in conc_words:
            found = True

            for wrd in normal_words:
                if br0 and br1:
                    if not BibleConcordance.objects.filter(trans = trans,\
                                                 word = wrd,\
                                                 book = wrd_rec.book,\
                                                 chapter = wrd_rec.chapter,\
                                                 verse = wrd_rec.verse ).exists():
                        found = False
                        break

                else:
                    if not BibleConcordance.objects.filter(trans = trans,\
                                                 word = wrd,\
                                                 book = wrd_rec.book,\
                                                 chapter = wrd_rec.chapter,\
                                                 verse = wrd_rec.verse ).exists():
                        found = False
                        break
            # If found but make sure we are not getting duplicates of
            # verse print outs if the words occur twice or more in 
            # the same verse.
            if found and (wrd_rec.book.id != last_book or \
            wrd_rec.chapter != last_chapter or \
            wrd_rec.verse != last_verse):
                last_book = wrd_rec.book.id
                last_chapter = wrd_rec.chapter
                last_verse = wrd_rec.verse
                
                if mode=="phrase":
                    verse_text = BibleVerses.objects.filter(trans = trans,
                         book=wrd_rec.book,
                         chapter = wrd_rec.chapter,
                         verse = wrd_rec.verse).first().verse_text

                    verse_words = strip_fluff_to_list(verse_text.lower()) 
                    logger.debug("phrase srch: verse_words = %s" % (str(verse_words),))
                    logger.debug("phrase srch: word_list = %s" % (str(word_list2),))
                    
                    if contains_sublist(verse_words, word_list2):

                        bv = BibleVerses.objects.filter(trans = trans,
                                                   book=wrd_rec.book,
                                                   chapter=wrd_rec.chapter,
                                                   verse=wrd_rec.verse)
                        verse_text = bv.first().verse_text

                       
                        logger.debug("In sublist")
                        yield {'index':sri, 'trans': trans.id, 'book': wrd_rec.book.id, 
                            'chapter': wrd_rec.chapter, 'verse': wrd_rec.verse,
                            'verse_text':verse_text }
                        sri += 1

                else: # mode == "simple"
                    found = True
                    if wild_words:
                        for wrd in wild_words:
                            mch = re.match("([a-zA-Z']+)\*$",wrd)
                            w = mch.group(1)
                            if not BibleConcordance.objects.filter(trans = trans,\
                                     book = wrd_rec.book,\
                                     chapter = wrd_rec.chapter,\
                                     verse = wrd_rec.verse )\
                                         .extra(where=["word like '%s%%'" % w])\
                                             .exists():
                                logger.debug("Word %s not found in %s,%d:%d" % (wrd, wrd_rec.book.long_book_name, wrd_rec.chapter, wrd_rec.verse))
                                found = False
                                break

                    if found:
                        # Add some markup around the search words

                        bv = BibleVerses.objects.filter(trans = trans,
                                                   book=wrd_rec.book,
                                                   chapter=wrd_rec.chapter,
                                                   verse=wrd_rec.verse)
                        verse_text = bv.first().verse_text
                        for wrd in normal_words:
                            verse_text = re.sub(r"("+wrd+")", 
                                                r"<word-match>\1</word-match>", 
                                                verse_text,
                                                flags = re.I)
                        for wrd in wild_words:
                            wrd = re.sub(r"\*", r"[a-zA-Z]*", wrd)
                            verse_text = re.sub(r"("+wrd+")", 
                                                r"<word-match>\1</word-match>", 
                                                verse_text,
                                                flags = re.I)
                            
                        yield {'index': sri, 'trans': trans.id, 'book': wrd_rec.book.id, 
                           'chapter': wrd_rec.chapter, 'verse': wrd_rec.verse,
                           'verse_text':verse_text }
                        sri += 1

            



#    def noticed(self, user, channel, message):
#        """ Biblebot receives notice """
#        logger.debug('NOTICE: '+ message)
        
    def joined(self, channel):
        """ BibleBot joins room """
        # Add basic options to room setup
        flds = ( ( 'verselimit', 4 ),
                ( 'searchlimit', 4 ),
                ( 'default_translation', 'kjv' ),)

        network = self.network

        for option, value in flds:
            opt = get_room_option(network, channel, option)
            if not opt:
                set_room_option(network, channel, option, value)

    def left(self, channel):
        """ Called when bible bot leaves channel """
        network = self.network
        set_room_option(network, channel, 'active', 0)

    
    def book_names(self, regex, chan, nick, **kwargs):
        version = regex.group(1)
        trans = BibleTranslations.objects.get(name=version)
        book_names = []
        for bb in BibleBooks.objects.filter(trans = trans):
            book_names.append((str(bb.canonical), str(bb.long_book_name)))
            if len(book_names) >= 10:
                self.notice(nick, str(book_names)) 
                book_names = []
        self.notice(nick, str(book_names)) 
              
    def versions(self, regex, chan, nick, **kwargs):
 
        translations = self._get_translations()
        tr_str = ",".join(translations)
        self.msg(chan, "Supported translations are %s " % (tr_str,))     
    def view_xrefs(self, regex, chan, nick, **kwargs):
        if nick.lower() not in self.xref_views:
            self.say(chan, "*** You need to find xrefs first ***")
            return

        refs = self.xref_views[nick.lower()][0:3]
        del self.xref_views[nick.lower()][0:3]
        trans_name = self._get_defaulttranslation(chan, nick)
        trans = BibleTranslations.objects.get(name = trans_name)
        if not refs:
            self.say(chan, "*** No more refs to view ***")
            return

        for ref in refs:
            book_name, refwork = ref.split(' ')
            ref1 = refwork.split('-')[0]
            chap, vs = ref1.split(':')
            
            book =  BibleBooks.objects.get(trans = trans, canonical = book_name)
            verse = BibleVerses.objects.get(trans = trans,
                                            book = book,
                                            chapter = chap,
                                            verse = vs)
            msg = u"{} {}:{} {}".format(book.long_book_name,
                                       chap,
                                       vs,
                                       verse.verse_text)

            self.say(chan, msg)                                            
            

        

               
    @irc_network_permission_required('set_pvt_version')
    def set_pvt_translation(self, regex, chan, nick, **kwargs):
        trans = regex.group(1)
        translations = self._get_translations()                        
        if trans not in translations:
            self.msg(chan, "Could not locate translation %s " % (def_trans,))
            return True
        else:
            set_global_option('pvt-translation', trans)
            self.msg(chan, "Private translation set to %s " % (trans,))   
                             
    @irc_room_permission_required('set_default_translation')
    def set_default_trans(self, regex, chan, nick, **kwargs):
        room = regex.group('room')
        def_trans = regex.group(2)
        translations = self._get_translations()                        
        if def_trans not in translations:
            self.msg(chan, "Could not locate translation %s " % (def_trans,))
            return
        else:
            set_room_option(self.factory.network, room, \
                'default_translation', def_trans)

            self.msg(chan, "Default translation for %s set to %s " % (room,def_trans)) 
                           
    @irc_room_permission_required('set_verse_limits')
    def set_search_limit(self, regex, chan, nick, **kwargs):
        room = regex.group('room')
        searchlmt = int(regex.group(2))
        # Get the channel the user is authorised to access
        
        if searchlmt > 20:
            self.msg(chan, "Search limit cannot be set higher than 20")
        else:
            set_room_option(self.factory.network, room, \
                'searchlimit', searchlmt)                        

            self.msg(chan, "Search limit for %s set to %s " % (room, searchlmt)) 
                   
    @irc_room_permission_required('set_verse_limits')
    def set_verse_limit(self, regex, chan, nick, **kwargs):
        room = regex.group('room')
        verselmt = int(regex.group(2))
        if verselmt > 20:
            self.msg(chan, "Verse limit cannot be set higher than 20")
        else:
            set_room_option(self.factory.network, room, \
                'verselimit', verselmt)

            self.msg(chan, "Verse limit for %s set to %s " % (room,verselmt)) 
                           
    def random_verse(self, regex, chan, nick, **kwargs):
        try:
            translation = regex.group('translation')
        except IndexError:
            translation = self._get_defaulttranslation(chan, nick)
            #translation = get_room_option(self.factory.network, chan, "default_translation")
        
        try:
            trans = BibleTranslations.objects.get(name = translation)
        except BibleTranslations.DoesNotExist:
            self.say(chan, "Translation {} not known".format(translation))
            return
        # Find first index of Genesis and last index of Revelation
        verse_range_data = BibleVerses.objects.filter(trans = trans).aggregate(Min('id'), Max('id'))
        v1 = verse_range_data['id__min']
        v2 = verse_range_data['id__max']
        
        random_scripture = BibleVerses.objects.filter(id__gte = v1, id__lt = v2).order_by("?").first()
        trans_name = random_scripture.trans.name
        book_name = random_scripture.book.long_book_name
        vs_text = random_scripture.verse_text
        
        random_vs = "{} {} {}:{} {}".format(trans_name.upper(),
                                            book_name,
                                            random_scripture.chapter,
                                            random_scripture.verse,
                                            vs_text)
                                            
        self.say(chan, random_vs)
        
        
    def dict(self, regex, chan, nick, **kwargs):

        lookup = regex.group(1)
        lookup = lookup.upper()

        try:
            dict_obj = BibleDict.objects.get(strongs=lookup)
            description = dict_obj.description
            self.say(chan, description)
            signal_data = {'chan': chan, 'nick': nick, 'strongs':lookup, 'dict':description }
            self.signal("dict_lookup", signal_data)

        except BibleDict.DoesNotExist:
            self.say(chan, "Sorry %s not found" % lookup)
    
    def search(self, regex, chan, nick, **kwargs):
          
        searchlimit = self._get_searchlimit(chan)
         
        words = [x.lower() for x  in regex.group(1).strip().split(' ')]

        def_trans = self._get_defaulttranslation(chan, nick)
        parse_res = self._parse_trans_book_range(def_trans, words)            

        if len(words) == 0:
            self.msg(chan, "Must have at least one word for search")
#            self.usage(chan, 'search')
            
        else:
            trans = parse_res['translation']
            
            book_range = ( parse_res['book_start'],
                           parse_res['book_end'] )
            
            book_range_s = self._stringify_book_range(trans, book_range)

            self.msg(chan,  "searching for \"" +  ", ".join(words) +"\"" + \
                " in " + trans.upper() + " " + book_range_s + " ....")
                                
            trans = BibleTranslations.objects.get(name=trans)

            gen = self._concordance_generator(chan, nick, trans, book_range, 
                                words, mode="simple")
            if chan.lower() not in self.pending_searches:
                self.pending_searches[chan.lower()] = {nick.lower():{}}
            
            if nick.lower() not in self.pending_searches[chan.lower()]:
                self.pending_searches[chan.lower()][nick.lower()] = {}
                
            self.pending_searches[chan.lower()][nick.lower()]['gen'] = gen
                
            finished = self._format_search_results(chan, nick.lower())
            if finished:
                del self.pending_searches[chan.lower()][nick.lower()]
    
    def next_search(self, regex, chan, nick, **kwargs):

        if nick.lower() in self.pending_searches[chan.lower()]:
            gen = self.pending_searches[chan.lower()][nick.lower()]['gen']
            delayed = self.reactor.callLater(3.5, self._search_long_time, chan, nick)
            self.pending_searches[chan.lower()][nick.lower()]['delayed'] = delayed
            finished = self._format_search_results(chan, nick.lower())
            if finished:
                del self.pending_searches[chan.lower()][nick.lower()]
        else:
            self.say(chan, "*** There is no currently active search***") 
                       
    def phrase_search(self, regex, chan, nick, **kwargs):
        
        phrase = regex.group(2)
        ref = regex.group(1)
        searchlimit = self._get_searchlimit(chan)
        words = [x.lower() for x  in phrase.strip().split(' ')]
        ref_words = [x.lower() for x in ref.strip().split(' ')]
        def_trans = self._get_defaulttranslation(chan, nick)
        parse_res = self._parse_trans_book_range(def_trans, ref_words)
        
        if len(words) == 0:
            self.msg(chan, "Error: Must have at least one word for "+act+"search")
        else:
            selected_trans = parse_res['translation']
            
            
            book_range = ( parse_res['book_start'],
                           parse_res['book_end'] )
            book_range_s = self._stringify_book_range(selected_trans, book_range)
            
            self.say(chan, "searching for phrase...\"%s\" in %s %s" % (phrase,selected_trans.upper(),book_range_s))                                
            trans = BibleTranslations.objects.get(name=selected_trans)
            gen = self._concordance_generator(chan, nick, trans, 
                    book_range, words, mode="phrase")
            if chan.lower() not in self.pending_searches:
                self.pending_searches[chan.lower()] = {nick.lower():{}}
            
            self.pending_searches[chan.lower()][nick.lower()]['gen'] = gen
            delayed = self.reactor.callLater(3.5, self._search_long_time, chan, nick)    
            self.pending_searches[chan.lower()][nick.lower()]['delayed'] = delayed
            self._format_search_results(chan, nick.lower())
    
    
    def _get_colour(self, chan, elmt):
        return None
#        try:
#            clr = BibleColours.objects.get(network=self.network, room=chan,
#                                    element=elmt)
#            return clr.mirc_colour
#        except BibleColours.DoesNotExist:
#            return None

    def xref(self, regex, chan, nick, **kwargs):
        passage_ref = regex.group(1).lower().strip()
        # mch1 = re.match(r"([a-z\+]+)\s+([1-3]?\s*[a-z]+)\s+(.*)", passage_ref)
        mch = re.match(r"([1-3]?\s*[a-z]+)\s+(.*)", passage_ref)
        if not mch:
            raise CommandException(nick, chan, \
                        "Could not decipher scripture xref " +\
                        "reference.  Format is " +\
                        "<book> <chapter>:<verse>")

        assert mch.lastindex == 2

        bookwork = mch.group(1)
        versework = mch.group(2)

        # remove possible spaces between books like "1 John" etc
        book = get_book(None, bookwork)
        if not book:
            raise CommandException(user, chan, "Could not find book %s" % (bookwork,))


        # remove embedded spaces
        passage = re.sub(r"(\d+)\s*:\s*(\d+)",r"\1:\2",versework)

        splitwork = re.split('(?::|-|\s+)',passage)
        chapter = int(splitwork.pop(0))
        if splitwork:
            verse = int(splitwork.pop(0))
        else:
            raise CommandException(nick, chan, \
                        "Too many arguments on line")

        xrefs = XRefs.objects.filter(primary_book = book,
                primary_chapter = chapter,
                primary_verse = verse ).order_by('-votes')
        xref_list = []
        for xref in islice(xrefs, 20):
            if xref.xref_book2:
                s = "{} {}:{}-{}:{}".format(xref.xref_book1, xref.xref_chapter1, xref.xref_verse1, 
                    xref.xref_chapter2, xref.xref_verse2)
            else:
                s = "{} {}:{}".format(xref.xref_book1, xref.xref_chapter1, xref.xref_verse1)
            xref_list.append(s)
        self.xref_views[nick.lower()] = xref_list
        xref_resp = ", ".join(xref_list)
        self.say(chan, xref_resp)
        
    def verse_lookup(self, regex, chan, nick, **kwargs):

        user = kwargs['user']
        msg = kwargs['clean_line']
        
        normal_colours = []
        normal_colours.append(self._get_colour(chan, "normal-translation"))
        normal_colours.append(self._get_colour(chan, "normal-verse-ref"))
        normal_colours.append(self._get_colour(chan, "normal-verse-text"))
        try:
            result = self._get_verses(chan, nick, user, msg)
        except BibleBooks.DoesNotExist:
            self.say(chan, "Book does not exist in this translation")
            return
        signal_data = {'nick':nick, 'chan':chan, 'verses':result}
        self.signal("verse_lookup", signal_data)
        for resp in result:
            clr_reply = []
            normal_colours1 = copy.copy(normal_colours)
            for elmt in resp:
                clr = normal_colours1.pop(0)
                if clr == None:
                    clr_reply.append(elmt)
                else:
                    fg,bg = clr.split(",")
                    clr_reply.append("\x03{},{} ".format(fg,bg)+elmt+" \x03")
            reply = ' '.join(clr_reply)
            logger.debug(repr(reply))
            self.say(chan, reply.encode("utf-8", "replace_spc"))

    def next(self, regex, chan, nick, **kwargs):
        
        result = self._next_reading(chan, nick)
        signal_data = {'nick':nick, 'chan':chan, 'verses':result}
        self.signal("verse_lookup", signal_data)
        if result:
            for resp in result:
                reply = ' '.join(resp)
                self.say(chan, reply)            
        else:
            self.say(chan, "No more verses to read")   
    

            
    def _parse_trans_book_range(self, def_trans, words):
        results = {}

        results['book_start'] = None
        results['book_end'] = None
        translations = self._get_translations()
        trans1 = words[0]
        if trans1 in translations:
            results['translation'] = trans1
            words.pop(0)
        else:
            results['translation'] = def_trans
        if len(words) == 0:
            return results
        
        mch = re.match('([1-3]?[a-z]+)$', words[0], re.I)
        mch2 = re.match('([1-3]?[a-z]+)-([1-3]?[a-z]+)$', words[0], re.I)
        if mch2:
            bk_s = mch2.group(1)
            bk_e = mch2.group(2)
            if get_book(results['translation'], bk_s) and \
            get_book(results['translation'], bk_e):
                results['book_start'] = bk_s
                results['book_end'] = bk_e
                words.pop(0)
        elif mch:
            bk = mch.group(0).lower()
            if get_book(results['translation'], bk):
                results['book_start'] = words.pop(0)
                results['book_end'] = results['book_start']
            elif bk == 'nt':
                results['book_start'] = 'mat'
                results['book_end'] = 'rev'
                words.pop(0)
            elif bk == 'ot':
                results['book_start'] = 'genesis'
                results['book_end'] = 'malachi'
                words.pop(0)
                
        return results
    
    def _search_long_time(self, chan, nick):
        logger.info("_search_long_time called with %s" % str((chan, nick)))
    
    def _search_results(self, chan, nick, results, finished):
        start_time = self.pending_searches[chan.lower()][nick.lower()]['timestamp']
        elapsed = time.clock() - start_time 
        signal_data = {'chan': chan, 'nick': nick, 'verses':results }
        self.signal("verse_search", signal_data)
        for result in results:
            # remove all <word-match> tags from result stream
            # (Not yet implemented anyway.)
            result = re.sub(r"<[^>]*>", "", result)
            self.say(chan, result)
            
        if finished:
            self.say(chan, "*** No more search results")
   
        self.say(chan, "Query took %6.3f seconds " % (elapsed,))
                    
    def _threaded_search_results(self, chan, nick, gen):
        results = []
        finished = False
        srch_limit = self._get_searchlimit(chan)
        for ii in range(0,srch_limit):
            try:
                res = gen.__next__()
                trans = BibleTranslations.objects.get(pk=res['trans'])
                book = BibleBooks.objects.get(pk=res['book'])
                idx = res['index']
                chptr = res['chapter']
                vrse = res['verse']
                verse_txt = res['verse_text']
                
                verse_ref = "{} {}:{}".format(book.long_book_name, chptr, vrse)

                clr = self._get_colour(chan, "search-translation")
                if clr:
                    fg,bg = clr.split(",")
                    trans_name = "\x03{},{} ".format(fg,bg)+trans.name.upper()+" \x03"
                else:
                    trans_name = trans.name.upper()
                    
                clr = self._get_colour(chan, "search-verse-ref")
                if clr:
                    fg,bg = clr.split(",")
                    verse_ref = "\x03{},{} ".format(fg,bg)+verse_ref+" \x03"
                
                clr = self._get_colour(chan, "search-verse-text")
                clr_words = self._get_colour(chan,"search-words")
                if clr:
                    fg,bg = clr.split(",")
                    prefix_clr = "\x03{},{}".format(fg,bg)
                if clr_words:
                    fgw,bgw = clr_words.split(",")
                    prefix_clw = "\x03{},{}".format(fg,bg)
                pieces2 = re.findall(r"<word-match>([^<]+?)</word-match>",verse_txt)
                if len(pieces2) > 0:
                    pieces1 = re.split(r"<word-match>[^<]+?</word-match>",verse_txt)
                pieces2.append("")

                # temporary hack until phrase search has markup
                if 'pieces1' in locals():
                    assert (len(pieces1) == len(pieces2))
                    # Here we rely on re.split returning the first list element
                    # as an empty string if the word match occurs at the beginning
                    # of the string which seems to be the case
                    txt = ""

                    for piece1, piece2 in zip(pieces1, pieces2):
                        if clr and piece1 != '':
                            txt += "\x03{},{}{}\x03".format(fg,bg,piece1)
                        elif not clr:
                            txt += piece1
                        if clr_words and piece2 != '':
                            txt += "\x03{},{}{}\x03".format(fgw,bgw,piece2)
                        elif not clr_words:
                            txt += piece2
                else:
                    txt = verse_txt
                    
                resp = "[%d] %s %s %s" % (idx, trans_name, verse_ref, txt)
                logger.debug( repr(resp))
                results.append(resp)

            except StopIteration:
#                self.say(chan, "*** No more search results")
                finished = True
                
        self._search_results(chan, nick, results, finished)

                    
    def _format_search_results(self, chan, nick):
        start_time = time.clock()
        self.pending_searches[chan.lower()][nick.lower()]['timestamp'] = start_time
        gen = self.pending_searches[chan.lower()][nick.lower()]['gen']        
        results = self._threaded_search_results(chan, nick, gen)
            
#        if chan != '%shell%' and THREADED_SEARCH:
#            results = await loop.run_in_executor(self._threaded_search_results, chan, nick, gen)
#        else:
#            results = self._threaded_search_results(chan, nick, gen)
#            

    def _stringify_book_range(self, version, book_range):
        if book_range[0] == None:
            return "Gen-Rev"
        elif book_range[1] == None:
            bk = get_book(version, book_range[0])
            return bk
        else:
            bk1 = get_book(version, book_range[0])
            bk2 = get_book(version, book_range[1])
            if bk1 == bk2:
                return bk1
            else:
                return bk1 + "-" + bk2
            
