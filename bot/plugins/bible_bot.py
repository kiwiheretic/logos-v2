#  BibleBot
import datetime
import re
import time
import copy
import threading

import pdb
from logos.pluginlib import Registry
from logos.constants import PUNCTUATION, STOP_WORDS

from bot.pluginDespatch import Plugin, CommandException
from logos.roomlib import get_room_option, set_room_option, set_global_option, \
    get_global_option
from logos.pluginlib import CommandDecodeException
from logos.models import BibleTranslations, BibleBooks, BibleVerses, \
    BibleConcordance, BibleDict
from _booktbl import book_table

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

class BibleBot(Plugin):

    # stop words are words that are so common that they
    # are not indexed (in the concordance).  It makes for a lot
    # smaller concordance database.
    stop_words = STOP_WORDS

    def __init__(self, *args):
        super(BibleBot, self).__init__(*args)
        
        
        # pending_searches used to remember
        # where up to with users searches
        # so that when they type !next it
        # follows on logically
        self.pending_searches = {}
        
        self.reading_progress = {}
    
    def _get_translations(self):
        trans = BibleTranslations.objects.all()    
        trans_list = []
        for tr in trans:
            trans_list.append(tr.name)
        return trans_list
    
    def _get_defaulttranslation(self, channel):
        if channel[0] == '#':
            res = get_room_option(self.network, channel,'default_translation')
        else:
            res = get_global_option('pvt-translation')
        if not res:
            res = 'kjv' # default translation
            
        return str(res)

    def _get_verselimit(self,channel):
        """ Get maximum number of verses that may be shown in room at one
        bot command """

        res = get_room_option(self.network, channel, "verselimit")

        if not res:
            res = 4 # default verselimit
        return res

    def _get_searchlimit(self, channel):
        """ Get the maximum numbers of verses to be shown while
        doing a search in this room """
        res = get_room_option(self.network, channel, "searchlimit")
        if not res:
            res = 5 # default search limit setting
        return int(res)

    def _get_verses(self, chan, nick, user, passage_ref):
        """ Retrieve the passage using the passage lookup supplied.
        This will look something like "nasb john 3:3-5"
        """
        
        # Get the maximum number of verses to display in one
        # go for the current room
        verselimit = int(self._get_verselimit(chan))

        # Find default translation for the current room
        def_trans = self._get_defaulttranslation(chan)

        #available_trans = BibleTranslations.objects.all()
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
            trans_id = BibleTranslations.objects.get(name = version).pk
        except BibleTranslations.DoesNotExist:
            raise CommandException(nick, user, "Unknown translation %s" % (version,))

        # remove possible spaces between books like "1 John" etc
        book = self._get_book(version, bookwork)
        if not book:
            raise CommandException(user, chan, "Could not find book %s" % (bookwork,))

        #passage = re.sub("\s+","", versework)
        passage = versework


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


             

        book_db = BibleBooks.objects.get(trans_id = trans_id,
                                         canonical = book)
        book_id = book_db.pk
        long_book_name = book_db.long_book_name
        

        # get qualifying verses
        qual_verses = BibleVerses.objects.filter(trans_id = trans_id,
                                   book = book_id,
                                   chapter = int(chapter),
                                   verse__gte = firstverse,
                                   verse__lt = firstverse+versecount)

        for v in qual_verses:
            pk = v.pk
        qual_verses_next_pk = pk + 1

        resp = []
        for q in qual_verses:
            resp.append((version.upper(),
                        long_book_name.capitalize() + " " + str(q.chapter) \
                            + ":" + str(q.verse),
                        q.verse_text))
        timestamp = datetime.datetime.now()

        self.reading_progress[nick.lower()] = \
            {'verses_pk':qual_verses_next_pk,
             'timestamp': timestamp}


        return resp
    
    def _next_reading(self, chan, user):
        if user.lower() not in self.reading_progress:
            self.say(chan, "No previous verse to read from")
        else:
            verses_pk = self.reading_progress[user.lower()]['verses_pk']
            qual_verses = BibleVerses.objects.filter(pk__gte = verses_pk)
            # Get the maximum number of verses to display in one
        # go for the current room
        verselimit = self._get_verselimit(chan)
        
        resp = []
        qual_verses_next_pk = None
        for q in qual_verses[0:verselimit]:
            resp.append((q.trans_id.name.upper(),
                        q.book.long_book_name.capitalize() + " " + str(q.chapter) \
                            + ":" + str(q.verse),
                        q.verse_text))
            qual_verses_next_pk = q.pk + 1
        
        timestamp = datetime.datetime.now()

        if qual_verses_next_pk:
            self.reading_progress[user.lower()] = \
                {'verses_pk':qual_verses_next_pk,
                 'timestamp': timestamp}
        else:
            del self.reading_progress[user.lower()]
        return resp
    
    def _concordance_generator(self, chan, nick, trans, book_range, words, mode="simple"):

        sri = 1  # This is the search result index
        
        if book_range[0]:
            bk = self._get_book(trans.name, book_range[0])
            br0 = BibleBooks.objects.filter(trans_id = trans, canonical=bk)\
                .first()
        else:
            br0 = None
        if book_range[1]:
            bk = self._get_book(trans.name, book_range[1])
            br1 = BibleBooks.objects.filter(trans_id = trans, canonical=bk)\
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
                    filter(trans_id = trans, book__gte = br0, 
                           book__lte = br1)
            else:
                q_results = BibleConcordance.objects.filter(trans_id = trans)
            
            if len(normal_words) > 0:
                s = "word in (" + ", ".join('\'{0}\''.format(w) for w in normal_words) +")"
                logger.info("where clause is \""+s +"\"")
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
                    filter(trans_id = trans, book__gte = br0, book__lte = br1)\
                    .extra(where=["word like '%s%%'" % w])\
                    .order_by('book', 'chapter', 'verse')
            else:
                conc_words = BibleConcordance.objects.\
                    filter(trans_id = trans, book__gte = br0, book__lte = br1,\
                    word = wrd).order_by('book', 'chapter', 'verse')
        # Otherwise 
        else:
            # Is this word a wildcard word?
            if mch: 
                w = mch.group(1)
                conc_words = BibleConcordance.objects.filter(trans_id = trans)\
                    .extra(where=["word like '%s%%'" % w])\
                    .order_by('book', 'chapter', 'verse')

            else:           
                conc_words = BibleConcordance.objects.filter(trans_id = trans,
                    word = wrd).order_by('book', 'chapter', 'verse')
        logger.debug("Number of concordance occurrences of word %s = %d" % (wrd, len(conc_words),))
        
        last_book = None
        last_chapter = None
        last_verse = None

        for wrd_rec in conc_words:
            found = True

            for wrd in normal_words:
                if br0 and br1:
                    if not BibleConcordance.objects.filter(trans_id = trans,\
                                                 word = wrd,\
                                                 book = wrd_rec.book,\
                                                 chapter = wrd_rec.chapter,\
                                                 verse = wrd_rec.verse ).exists():
                        found = False
                        break

                else:
                    if not BibleConcordance.objects.filter(trans_id = trans,\
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
                    verse_text = BibleVerses.objects.filter(trans_id = trans,
                         book=wrd_rec.book,
                         chapter = wrd_rec.chapter,
                         verse = wrd_rec.verse).first().verse_text

                    verse_words = strip_fluff_to_list(verse_text.lower()) 
                    logger.debug("phrase srch: verse_words = %s" % (str(verse_words),))
                    logger.debug("phrase srch: word_list = %s" % (str(word_list2),))
                    
                    if contains_sublist(verse_words, word_list2):
                        logger.debug("In sublist")
                        yield {'index':sri, 'trans': trans.id, 'book': wrd_rec.book.id, 
                            'chapter': wrd_rec.chapter, 'verse': wrd_rec.verse }
                        sri += 1

                else: # mode == "simple"
                    found = True
                    if wild_words:
                        for wrd in wild_words:
                            mch = re.match("([a-zA-Z']+)\*$",wrd)
                            w = mch.group(1)
                            if not BibleConcordance.objects.filter(trans_id = trans,\
                                     book = wrd_rec.book,\
                                     chapter = wrd_rec.chapter,\
                                     verse = wrd_rec.verse )\
                                         .extra(where=["word like '%s%%'" % w])\
                                             .exists():
                                logger.debug("Word %s not found in %s,%d:%d" % (wrd, wrd_rec.book.long_book_name, wrd_rec.chapter, wrd_rec.verse))
                                found = False
                                break

                    if found:
                        yield {'index': sri, 'trans': trans.id, 'book': wrd_rec.book.id, 
                           'chapter': wrd_rec.chapter, 'verse': wrd_rec.verse }
                        sri += 1

            



    def noticed(self, user, channel, message):
        """ Biblebot receives notice """
        logger.info('NOTICE: '+ message)
        
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

    def privmsg(self, user, channel, message):
        pass

    def command(self, nick, user, chan, orig_msg, msg, act):
        activator = re.escape(act)
        next_mch = re.match('(next|n)\s*$', msg)
        search_mch = re.match('(?:search|s)\s+(.+)', msg)
        phrase_search_mch = re.match('(?:search|s)\s+([^"]*)\"([^"]+)\"', msg)
        next_search_mch = re.match('(?:search|s)\s*$', msg)
        default_trans_mch = re.match('set\s+default\s+translation\s+([a-zA-Z]+)', msg)
        pvt_trans_mch = re.match('set\s+(?:private|pvt)\s+translation\s+([a-zA-Z]+)', msg)
        set_searchlimit_mch = re.match('set\s+search\s+limit\s+(\d+)\s*$', msg)
        set_verselimit_mch = re.match('set\s+verse\s+limit\s+(\d+)\s*$', msg)
        versions_mch = re.match('(?:translations|versions)\s*$', msg)
        dict_mch = re.match('dict\s+(\S+)', msg)

        # match "KJV John 3:16, John 3:16, John 3 16, John 3", etc...
        # also "KJV 1 John 3:16" or "KJV+ john 3:16"
        # Note the parenthesis matching captured groups are not  used.  
        # It is just a convenience to not clutter up the regex
        verse_mch = re.match('(\w+\+?\s+)?\d?\s*[a-zA-Z]+\s+\d+\s*(:?\s*\d+\s*(-?\s*\d+)?)?$',\
                              msg)
        help_mch = re.match('help',msg)
        
        book_names_mch = re.match('book names (?:for )?(?:translation|version)\s+(.*)', msg)
        if versions_mch: 
            translations = self._get_translations()
            tr_str = ",".join(translations)
            self.msg(chan, "Supported translations are %s " % (tr_str,))
        elif help_mch:
            self.msg(chan, "For help see https://biblebot.wordpress.com/user-instructions/")
        elif default_trans_mch:
            ch = Registry.authorized[nick]['channel']
            def_trans = default_trans_mch.group(1)
            translations = self._get_translations()                        
            if def_trans not in translations:
                self.msg(chan, "Could not locate translation %s " % (def_trans,))
                return
            else:
                set_room_option(self.factory.network, ch, \
                    'default_translation', def_trans)

                self.msg(chan, "Default translation for %s set to %s " % (ch,def_trans))
            return True
        elif pvt_trans_mch:
            if nick in Registry.sys_authorized:
                trans = pvt_trans_mch.group(1)
                translations = self._get_translations()                        
                if trans not in translations:
                    self.msg(chan, "Could not locate translation %s " % (def_trans,))
                    return True
                else:
                    set_global_option('pvt-translation', trans)
                    self.msg(chan, "Private translation set to %s " % (trans,))
            return True
        elif set_verselimit_mch:
            verselmt = int(set_verselimit_mch.group(1))
            ch = Registry.authorized[nick]['channel']

            if verselmt > 20:
                self.msg(chan, "Verse limit cannot be set higher than 20")
            else:
                set_room_option(self.factory.network, ch, \
                    'verselimit', verselmt)

                self.msg(chan, "Verse limit for %s set to %s " % (ch,verselmt))
            return True
        elif set_searchlimit_mch:
            searchlmt = int(set_searchlimit_mch.group(1))
            ch = Registry.authorized[nick]['channel']

            if searchlmt > 20:
                self.msg(chan, "Search limit cannot be set higher than 20")
            else:
                set_room_option(self.factory.network, ch, \
                    'searchlimit', searchlmt)                        

                self.msg(chan, "Search limit for %s set to %s " % (ch, searchlmt))
            return True
                
        elif book_names_mch:
            version = book_names_mch.group(1)
            trans = BibleTranslations.objects.get(name=version)
            book_names = []
            for bb in BibleBooks.objects.filter(trans_id = trans):
                book_names.append((str(bb.canonical), str(bb.long_book_name)))
            self.msg(chan, str(book_names))
            return True
        
        elif phrase_search_mch:
            phrase = phrase_search_mch.group(2)
            ref = phrase_search_mch.group(1)
            searchlimit = self._get_searchlimit(chan)
            words = [x.lower() for x  in phrase.strip().split(' ')]
            ref_words = [x.lower() for x in ref.strip().split(' ')]
            def_trans = self._get_defaulttranslation(chan)
            parse_res = self._parse_trans_book_range(def_trans, ref_words)
            
            if len(words) == 0:
                self.msg(chan, "Error: Must have at least one word for "+act+"search")
            else:
                selected_trans = parse_res['translation']
                self.say(chan, "searching for phrase...\"%s\" in %s" % (phrase,selected_trans.upper()))
                
                book_range = ( parse_res['book_start'],
                               parse_res['book_end'] )
                                    
                trans = BibleTranslations.objects.get(name=selected_trans)
                gen = self._concordance_generator(chan, nick, trans, 
                        book_range, words, mode="phrase")
                if chan.lower() not in self.pending_searches:
                    self.pending_searches[chan.lower()] = {}
                
                self.pending_searches[chan.lower()][nick.lower()] = gen
                self._format_search_results(chan, gen)
        elif search_mch:

            searchlimit = self._get_searchlimit(chan)
             
            words = [x.lower() for x  in search_mch.group(1).strip().split(' ')]

            def_trans = self._get_defaulttranslation(chan)
            parse_res = self._parse_trans_book_range(def_trans, words)            

            if len(words) == 0:
                self.msg(chan, "Must have at least one word for "+act+"search")
                self.usage(chan, 'search')
                
            else:
                trans = parse_res['translation']
                
                book_range = ( parse_res['book_start'],
                               parse_res['book_end'] )
                self.msg(chan,  "searching for \"" +  ", ".join(words) +"\"" + \
                    " in " + trans.upper() + " ....")
                                    
                trans = BibleTranslations.objects.get(name=trans)

                gen = self._concordance_generator(chan, nick, trans, book_range, 
                                    words, mode="simple")
                if chan.lower() not in self.pending_searches:
                    self.pending_searches[chan.lower()] = {}
                
                self.pending_searches[chan.lower()][nick.lower()] = gen
                    
                    
                self._format_search_results(chan, gen)
                
        elif next_search_mch:
            gen = self.pending_searches[chan.lower()][nick.lower()]
            self._format_search_results(chan, gen)

        elif next_mch: # next reading
            result = self._next_reading(chan, nick)
            print result
            if result:
                for resp in result:
                    reply = ' '.join(resp)
                    self.say(chan, str(reply))            
            else:
                self.say(chan, "No more verses to read")            
        elif dict_mch:
            lookup = dict_mch.group(1)
            lookup = lookup.upper()

            try:
                dict_obj = BibleDict.objects.get(strongs=lookup)
                description = dict_obj.description
                self.say(chan, description)
            except BibleDict.DoesNotExist:
                self.say(chan, "Sorry %s not found" % lookup)

        elif verse_mch:
            result = self._get_verses(chan, nick, user, msg)
            print result
            for resp in result:
                reply = ' '.join(resp)
                self.say(chan, str(reply))

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
        
        mch = re.match('[1-2]?[a-z]+', words[0], re.I)
        mch2 = re.match('([1-2]?[a-z]+)-([1-2]?[a-z]+)', words[0], re.I)
        if mch2:
            bk_s = mch2.group(1)
            bk_e = mch2.group(2)
            if self._get_book(results['translation'], bk_s) and \
            self._get_book(results['translation'], bk_e):
                results['book_start'] = bk_s
                results['book_end'] = bk_e
                words.pop(0)
        elif mch:
            bk = mch.group(0).lower()
            if self._get_book(results['translation'], bk):
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
    def _format_search_results(self, chan, gen):
        start_time = time.clock()
        
        srch_limit = self._get_searchlimit(chan)
        for ii in range(0,srch_limit):
            try:
                res = gen.next()
                trans = BibleTranslations.objects.get(pk=res['trans'])
                book = BibleBooks.objects.get(pk=res['book'])
                idx = res['index']
                chptr = res['chapter']
                vrse = res['verse']
                verse_txt = BibleVerses.objects.get(trans_id = trans,
                                book = book, chapter = chptr,
                                verse = vrse).verse_text
                            
                str1 = "[%d] %s %s %d:%d : %s " % (idx, trans.name.upper(), book.long_book_name, 
                                              chptr, vrse, verse_txt)
                
                self.say(chan, str1)
            except StopIteration:
                self.say(chan, "*** No more search results")
                break
        elapsed = time.clock() - start_time    
        self.say(chan, "Query took %6.3f seconds " % (elapsed,))
        
    def _get_book(self, version, bookwork):
        
        # remove possible spaces between books like "1 John" etc
        book = re.sub("\s+", "", bookwork)
        
        bl = len(book)
        
        book_found = None
        for smallbk, bigbk in book_table:
            if smallbk == book:
                book_found = smallbk
                break
            if bigbk[0:bl] == book:
                book_found = smallbk
                break
        
        if not book_found:
            trans = BibleTranslations.objects.get(name=version)
            if BibleBooks.objects.filter(trans_id=trans, canonical = book).exists():
                return book
            else:
                return None
        
        return book_found

