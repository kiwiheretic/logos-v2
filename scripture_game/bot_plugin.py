# The one and only GameBot (tm)
#
# Written by SplatsCreations
# Date Written:  30th July 2009
# Email: splat@myself.com
#
# Uses twisted matrix from ----> http://twistedmatrix.com/
# if running on windows also needs the win32api module
# from ----> http://python.net/crew/mhammond/win32/
# but probably not if on linux but haven't tested it on linux yet.
#
# Developed using python version 2.6.5
# Written using Twisted version 8.2.0
# - if doesn't work and you have a twisted version less than that then
#   you will need a version upgrade
#
from __future__ import absolute_import
VERSION = 0.95
SCRIPTURE_COLOUR = ''
import string
# should be database agnostic - remove import
#import sqlite3
import random

#from time import clock
from bot.pluginDespatch import Plugin
from random import randint

from django.db import transaction
from django.db.models import Min, Max
from .models import GameGames, GameUsers, GameSolveAttempts
from bibleapp.models import BibleTranslations, BibleBooks, BibleVerses

import os
import re
import sys
import datetime
from optparse import OptionParser

#    Process commands from the user.  All messages directed to the bot
#    end up here.

#    Currently handles these commands:
#    !gamed played
#        - lists the games played in the database
#    !restart
#        - restart the currently selected game
#    !join
#        - join a multi-user game
#    !start
#        - start a multi-user game after everyone has joined
#    !stop
#    !end
#    !endgame
#        - stop a game that is in progress
        
import shutil
import logging
from django.conf import settings

from bibleapp.bot_plugin import get_book

logger = logging.getLogger(__name__)
logging.config.dictConfig(settings.LOGGING)

def blank_out_letters(letters, text):
    """ Takes a scripture and blanks out text with underscores
        except for letters"""
    lowers = string.lowercase[0:26]
    uppers = string.uppercase[0:26]

    
    show_letters = ''
    for ii in range(0,26):
        ch = chr(ord('a') + ii)
        if ch in letters:
            show_letters += ch
        else:
            show_letters += '-'
            
    for ii in range(0,26):
        ch = chr(ord('A') + ii)
        if ch.lower() in letters:
            show_letters += ch
        else:
            show_letters += '-'

    tr_table = string.maketrans(lowers+uppers, show_letters)
    
    resp = string.translate(text, tr_table)

    return resp


class ScriptureChallenge(Plugin):
    """ The class created by the factory class for handling non game specific
        commands """
    plugin = ('sg', 'Scripture Challenge Game')
    
    def __init__(self, *args):
        super(ScriptureChallenge, self).__init__(*args)
        
        self.commands = (\
            ('games played', self.games_played, "Change this description"),
            ('challenge', self.challenge, "Change this description"),
            ('examine\s+(\d+)', self.examine, "Change this description"),
            ('join', self.join, "Change this description"),
            ('start with (?P<translation>\w+)$', self.start1, "Change this description"),
            ('start with (?P<translation>\w+) (?P<book>\w+)', self.start1, "Change this description"),
            ('stop|end|endgame', self.stop, "Change this description"),
            ('restart', self.restart, "Change this description"),
            ('hash', self.hash, "Change this description"),
            )
        self.rooms_hash = {}
        
    def write_log (self, text):
        logger.info(text)

    def joined(self, chan):
        logger.info("Scripture challenge joined %s" % (chan,))
        self.rooms_hash[chan.lower()] = {}
        rooms_hash = self.rooms_hash[chan.lower()]
        rooms_hash['GameStarted'] = False
        rooms_hash['NicksInGame'] = []
        
               
    def userLeft(self, user, channel):
        """ 
        Called when I see another user leaving a channel.
        """
        self.write_log( "userLeft %s %s - deleting hash entry " % (channel, user))
        room_hash = self.rooms_hash[channel.lower()]

        NicksInGame = room_hash['NicksInGame']
        if user in NicksInGame:
            self.say(channel, user + " has left the game.")
            idx = room_hash['NickCurrentTurn']
            currTurnPlayer = NicksInGame[idx]
            nextPlayer = currTurnPlayer
            NicksInGame.remove(user)
        if len(NicksInGame) == 0:
            self.end_game(channel)
        elif user != currTurnPlayer:
            room_hash['NickCurrentTurn'] = NicksInGame.index(currTurnPlayer)
        else:
            # If it was the last player in the list that left and
            # it was his turn then special case.  Then we move to
            # the first player.
            if idx >= len(NicksInGame):
                room_hash['NickCurrentTurn'] = 0
            else:
                pass
            idx = room_hash['NickCurrentTurn']
            nextPlayer = NicksInGame[idx]
            self.say(channel, "Play moves to " + nextPlayer)
            # If its not the last player we don't need to do anything
            # as then when the list is reduced it moves to the next player
        room_hash['current_user'] = nextPlayer
        self.user_left(channel)
  
    def userQuit(self, user, quitMessage):
        """
        Called when I see another user disconnect from the network.
        """
        pass
          
  
        
    def userRenamed(self, oldname, newname):
        """
        A user changed their name from oldname to newname.
        """
        for room_hash in self.rooms_hash.values():
            NicksInGame = room_hash['NicksInGame']

            if oldname in NicksInGame:
                idx = NicksInGame.index(oldname)
                NicksInGame[idx] = newname


    def show_server_hash(self, channel):
        self.say(channel, "------ Server Hash ------")
        for k in self.rooms_hash.keys():
            self.say(channel, "  " + k + "   " + str(self.rooms_hash[k]))
        self.say(channel, "-------------------------")

            
    def reset_server_hash(self, channel):
        """ Stop any game in its tracks and reset back to no game """

        rooms_hash = self.rooms_hash[channel.lower()]
        rooms_hash['NickUsing'] = None
        rooms_hash['NicksInGame'] = []
        rooms_hash['NickCurrentTurn'] = 0
        rooms_hash['GameStarted'] = False
            
    def start_game(self, channel, nickname):
        """ Start or restart a game or a multi-user game """

        if channel not in self.rooms_hash:
            self.rooms_hash[chan.lower()] = {}
        rooms_hash = self.rooms_hash[chan.lower()]
        rooms_hash['NicksInGame'].append(nickname)
        rooms_hash['letters_given'] = []
        rooms_hash['currScrip'] = None
        rooms_hash['explain'] = None

        rooms_hash['round'] = 0
        rooms_hash['nickUsing'] = None
        rooms_hash['nicksInGame'] = []
        rooms_hash['nickCurrentTurn'] = 0
        rooms_hash['solve_state'] = None  # to enable @list to work on startup


        
        self.say(channel, "You are now playing Scripture Challenge ")
        self.say(channel, ' ')
        rooms_hash['active_game'].greeting(channel)
        
        rooms_hash['GameStarted'] = False
        self.say(channel, ' ')
        self.say(channel, 'Type !join now to participate in this game')
        self.say(channel, 'When everyone is ready type !start to begin')
    
    def privmsg(self, user, chan, msg):
        logger.debug("privmsg " + str((user, chan, msg)))

        short_nick = user.nick
        if chan.lower() in self.rooms_hash:
            rooms_hash = self.rooms_hash[chan.lower()]
            #
            # Make sure a user can only talk to game if its their turn
            # in a multi user game
            if rooms_hash['GameStarted']:
                Exp_Idx = rooms_hash['NickCurrentTurn']
                if Exp_Idx == None:
                    Expected_Nick = None
                else:
                    Expected_Nick = rooms_hash['NicksInGame'][Exp_Idx]
                if short_nick.lower() == Expected_Nick.lower():
                    self.handle_command(chan, short_nick,  msg)
                else:
                    self.non_turn_based_command(chan, short_nick,  msg)
                    
            
    def games_played(self, regex, chan, nick, **kwargs):
        self.game_list(chan)

    def challenge(self, regex, chan, nick, **kwargs):
        self.rooms_hash[chan.lower()] = {}
        rooms_hash = self.rooms_hash[chan.lower()]
        rooms_hash['GameStarted'] = False
        rooms_hash['NicksInGame'] = []
        rooms_hash['NickCurrentTurn'] = 0
        self.say(chan, "== Scripture Challenge Version %s ==" % (VERSION,))
        self.say(chan, " -- Courtesy of SplatsCreations")
        self.say(chan, " http://www.splats-world.pw/wp/chat/scripture-challenge-game/")  
              
    def examine(self, regex, chan, nick, **kwargs):
        game_id = int(regex.group(1))
        self.examine(chan, game_id)
        
    def join(self, regex, chan, nick, **kwargs):

        rooms_hash = self.rooms_hash[chan.lower()]
        if not rooms_hash['GameStarted']:
            # It is only meaningful to join a game once.
            if not nick.lower() in map(lambda x: x.lower(), rooms_hash['NicksInGame']):
                rooms_hash['NicksInGame'].append(nick)
                self.say(chan, nick + ' has joined game')
            else:
                self.say(chan, nick + ' has already joined game')
        else:
            self.say(chan, nick + ', game has already started, cannot join.')                            

    def start1(self, regex, chan, nick, **kwargs):
        
        translation = regex.group('translation')


        try:
            trans = BibleTranslations.objects.get(name = translation)
        except BibleTranslations.DoesNotExist:
            self.say(chan, "Translation {} not known".format(translation))
            return
            
        try:
            book_name = regex.group('book')
            book_name = get_book(translation, book_name)
        except IndexError:
            book_name = None
                 
        if book_name:
            book = BibleBooks.objects.get(trans = trans, canonical = book_name)
            verse_range_data = BibleVerses.objects.filter(trans = trans, book=book).aggregate(Min('id'), Max('id'))
        else:
            verse_range_data = BibleVerses.objects.filter(trans = trans).aggregate(Min('id'), Max('id'))
        v1 = verse_range_data['id__min']
        v2 = verse_range_data['id__max']
        
        rooms_hash = self.rooms_hash[chan.lower()]
        if 'NicksInGame' not in rooms_hash or \
            len(rooms_hash['NicksInGame']) == 0:
            self.say(chan, 'No one has yet joined game.')
            
        elif not rooms_hash['GameStarted']:
            
            NicksInGame = rooms_hash['NicksInGame']

            if 'NickCurrentTurn' in rooms_hash:
                NickCurrentTurn = rooms_hash['NickCurrentTurn']
            else:
                rooms_hash['NickCurrentTurn'] = 0
                NickCurrentTurn = 0

            CurrNick = NicksInGame[NickCurrentTurn]


            NickCurrentTurn = 0
            game = self._create_game(NicksInGame)

            self.say(chan, 'Game started...')
            self.say(chan, ' ')
            
            rooms_hash['game'] = game
            rooms_hash['current_user'] = CurrNick
            rooms_hash['Round'] = 0

            rooms_hash['GameStarted'] = True
            rooms_hash['NickCurrentTurn'] = NickCurrentTurn
            self.start(chan, v1, v2)

        else:
            self.chan(chan, 'Game already started')
        
    def stop(self, regex, chan, nick, **kwargs):
        self.end_game(chan)
        
    def restart(self, regex, chan, nick, **kwargs):
        self.start_game(nick)
        
    def hash(self, regex, chan, nick, **kwargs):
        self.show_server_hash(chan)  
      
    def _create_game(self, NicksInGame):
        # Record the new game to the database
        with transaction.atomic():
            game = GameGames()

            game.save()
            
            for nick in NicksInGame:
                host = self.irc_conn.nicks_db.get_host(nick)
                
                gu = GameUsers(game = game, nick = nick, host = host)
                gu.save() 
        return game
       
    def advance_user(self, chan):  
        """ callback from game module in multiuser game to advance to next user
            in a multi user game """

        rooms_hash = self.rooms_hash[chan.lower()]
        
        NicksInGame = rooms_hash['NicksInGame']
        NumNicks = len(rooms_hash['NicksInGame'])
        NickCurrentTurn = rooms_hash['NickCurrentTurn']
        
        NickCurrentTurn += 1
        if NickCurrentTurn >= NumNicks: 
            NickCurrentTurn = 0
            rooms_hash['Round'] += 1
        rooms_hash['NickCurrentTurn'] = NickCurrentTurn
        CurrNick = NicksInGame[NickCurrentTurn]
        logger.debug ( "advance user - next nick = "+ CurrNick)

        rooms_hash['current_user'] = CurrNick

    def end_game(self, channel, win=False):
        """ callback for when the game has come to a conclusion
            (ie win or lose).  When a game finishes we want to stop
            stuff from happening.  """
        
        rooms_hash = self.rooms_hash[channel.lower()]

        if rooms_hash['GameStarted']:
            self.say(channel, "Game Finished.")
            game = rooms_hash['game']
            # Find the winner if any
            if win:
                currTurn = rooms_hash['NickCurrentTurn']
                nick = rooms_hash['NicksInGame'][currTurn]

                winner = GameUsers.objects.get(game=game, nick=nick)
            else:
                winner = None
            
            with transaction.atomic():
                game.winner = winner
                game.num_rounds = rooms_hash['Round']
                game.save()

        self.reset_server_hash(channel)

            
    def send_reply(self, channel, msg):
        """ short hand method for sending message to channel """
        self.say(channel, msg)
        

    def examine(self, channel, game_id):
        """ examine the game """
        
        try:
            game = GameGames.objects.get(id = game_id)
        except GameGames.DoesNotExist:
            self.say(channel, "Game not in database")
            return
        
        usrs = [ user.nick for user in game.gameusers_set.all() ]
        dt = game.timestamp
        dstr = dt.strftime("%d-%b-%Y %I:%M%p")
        format_s = "[%s] %s ref=\"%s\" rounds = %s players = [ %s ]" % \
            (game.id, dstr, game.ref, game.num_rounds, ", ".join(usrs))
        format_s = str(format_s)
        self.say(channel, format_s)
                    
        attempts = [attempt for attempt in game.gamesolveattempts_set.all()]

        for attempt in attempts:
            fmt = str(" [%s] %s" % (attempt.id, attempt.user.nick))
            self.say(channel, fmt)
            self.say(channel, " attempt = \"%s\"" % str(attempt.attempt))            
            self.say(channel, " result = " + str(attempt.reason))
            
    
    def game_list(self, channel):
        """ !games played - list all games that the bot knows about """
        
        games = GameGames.objects.order_by('-timestamp').all()[:5]
        for game in games:
            dt = game.timestamp
            
            usrs = [ user.nick for user in game.gameusers_set.all() ]
            
            dstr = dt.strftime("%d-%b-%Y %I:%M%p")
            if game.winner:
                format_s = "[%s] %s ref=\"%s\" rounds=%s winner=%s players=[ %s ]" % \
                    (game.id, dstr, game.ref, game.num_rounds, game.winner.nick,
                     ", ".join(usrs))
            else:
                format_s = "[%s] %s ref=\"%s\" rounds = %s players=[ %s ]" % \
                    (game.id, dstr, game.ref, game.num_rounds, ", ".join(usrs))
            format_s = str(format_s)
            self.say(channel, format_s)
            

            usr_list = str("  User list : %s " % ", ".join(usrs))
            self.say(channel, usr_list)
        self.say(channel, "--- end of list ---")
            
            
    def greeting(self, channel):
        """ Called when the game is first started """
        self.say(channel, \
                "\x032This is the game of scripture challenge.  This is a multi user game " + \
                "but can also be played as a single user game. " + \
                "The object is to guess the scripture.  (Its a little bit like hangman " + \
                "and a bit like the TV show Jeopardy) " + \
                "Each player has turns at choosing a letter and after each letter has " + \
                "the option of solving the scripture.")
        self.say(channel, " ")
        self.say(channel, \
                "\x032 Type !redisplay to re-display the scripture at any time. " + \
                "This may be useful if the scripture has been scrolled off the " + \
                "top of the window. ")

    def _display_scripture(self, channel):
        rooms_hash = self.rooms_hash[channel.lower()]
        verse = rooms_hash['currScrip'].verse_text.encode("utf8", "replace")
        
        script_disp = blank_out_letters(rooms_hash['letters_given'],
                                         verse)
        self.say(channel, "The scripture as it currently stands:")
        self.say(channel, SCRIPTURE_COLOUR + script_disp)
        self.say(channel, rooms_hash['current_user'] + ', choose a letter by typing !<letter> where letter is a to z')
    
    def start(self, channel, begin_id, end_id):
        """ Called when the multi user game is ready to begin
            and all users have signed up """
        rooms_hash = self.rooms_hash[channel.lower()]
        rooms_hash['explain'] = None
        
        random_scripture = BibleVerses.objects.filter(id__gte = begin_id, id__lt = end_id).order_by("?").first()

        ref = "{} {}:{}".format(random_scripture.book.long_book_name,
                                random_scripture.chapter,
                                random_scripture.verse)
                                
                                
        text = random_scripture.verse_text
        logger.info('Scipture chosen : ' + ref + "," + text)
        
        rooms_hash['currScrip'] = random_scripture
        rooms_hash['currScrip'].ref = ref # slightly hacky
        tr_table = string.maketrans('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', '-' * (26*2))
        rooms_hash['letters_given'] = []

        game = rooms_hash['game']
        game.ref = ref
        game.scripture = text
        game.num_rounds = 0
        game.save()
        
        self._display_scripture(channel)
        rooms_hash['solve_state'] = None        
        
    def handle_command(self, channel, nick, command):
        rooms_hash = self.rooms_hash[channel.lower()]
        short_nick = nick.split('!')[0]
        
        letter_mch = re.match('^![a-z]\s*$|^[a-z]\s*$', command, re.IGNORECASE)
        if letter_mch:
            if letter_mch.group(0)[0] == '!':
                letter = letter_mch.group(0)[1].lower()
            else:
                letter = letter_mch.group(0)[0].lower()
            
            if letter in rooms_hash['letters_given']:
                self.say(channel, "This letter has already been chosen.")
                self.say(channel, rooms_hash['current_user'] + ', Please try again.')
            else:
                rooms_hash['letters_given'].append(letter)
                logger.debug('letters given = ' + str(rooms_hash['letters_given']))
                verse = rooms_hash['currScrip'].verse_text.encode("utf8", "replace")
                script_disp = blank_out_letters(rooms_hash['letters_given'], verse)
                self.say(channel, "The scripture as it currently stands:")
                self.say(channel, SCRIPTURE_COLOUR+script_disp)
                self.say(channel, rooms_hash['current_user'] + ', Do you wish to solve?  (Please type a yes or no answer)')
                rooms_hash['solve_state'] = "yes_no_answer"

        elif rooms_hash['solve_state'] == "yes_no_answer":
            yes_no_mch = re.match('^yes$|^no', command, re.IGNORECASE)
            if yes_no_mch:
                resp = yes_no_mch.group(0).lower()
                if resp == "no":
                    self.advance_user(channel)
                    rooms_hash['letters_given'].sort()
                    letters_given = str(rooms_hash['letters_given'])
                    self.say(channel, "Letters currently used are : " + letters_given)
                    self.say(channel, rooms_hash['current_user'] + ', choose a letter by typing !<letter> where letter is a to z')
                    rooms_hash['solve_state'] = None
                else:                
                    self.say(channel, "Type your answer being sure to get spelling correct")            
                    rooms_hash['solve_state'] = "solve_response"
        elif rooms_hash['solve_state'] == "solve_response":
            rooms_hash['solve_state'] = None
            # find the current nick by matching on nick in game_users
            # in database.  In future maybe use host name mask
            nick = rooms_hash['current_user']
            game = rooms_hash['game']
            user = GameUsers.objects.get(game = game, nick = nick)

            with transaction.atomic():            
                # If user hasn't renamed their nick (oh well)
                # (If they didn't we won't bother recording their attempt,
                # may change in future.)
                reason_str = ""
                gsa = GameSolveAttempts(game = game, user=user, 
                                        attempt = command.strip())
                user_words = re.split('\s+', command.strip())
                scrip_words = re.split('\s+',rooms_hash['currScrip'].verse_text.strip())
                
                uwl = len(user_words)
                swl = len(scrip_words)
                if uwl == swl:  # If we have the right number of words for the verse
                    scripMatch = True
                    for ii, wrd in enumerate(scrip_words):
                        uword = user_words[ii]
                        
                        iii = 0
                        isMatch = True
                        for ch in wrd:
                            if ch.isalpha():
                                while iii < len(uword):
                                   if uword[iii].isalpha(): break
                                   iii += 1
                                if (iii == len(uword)):
                                    isMatch = False
                                    break
                                if ch.lower() != uword[iii].lower():
                                    isMatch = False
                                    break
                                else:
                                    iii += 1
                        if not isMatch:
                            reason_str = "'%s' != '%s'" % (uword, wrd)
                            break
                    if scripMatch:
                        reason_str = "Correctly solved"
                        self.say(channel, "Well done you have correctly solved the scripture")
                        self.say(channel, rooms_hash['currScrip'].verse_text)
                        self.say(channel, rooms_hash['currScrip'].ref)
                        self.end_game(channel, win=True)
                    else:                                    
                        self.say(channel, "Sorry, your attempt at solving did not succeed")
                        # try this
                        if len(rooms_hash['NicksInGame']) > 1:
                            self.advance_user(channel)
                                
                            self._display_scripture(channel)
                            rooms_hash['solve_state'] = None                        
                        else:
                            # end of try
                            self.say(channel, rooms_hash['currScrip'].verse_text)
                            self.say(channel, rooms_hash['currScrip'].ref)
                            self.end_game(channel) 
                        
                else:
                    reason_str = "word count mismatch"
                     
                    
      
                    if len(rooms_hash['NicksInGame']) > 1:
                        self.say(channel, "Sorry, your attempt at solving did not succeed")
                        self.advance_user(channel)
                        
                        self._display_scripture(channel)
                        rooms_hash['solve_state'] = None
                        
                    else:
                        # end of try

                        self.say(channel, "Sorry, you did not have the correct number of words")
                        self.say(channel, rooms_hash['currScrip'].verse_text)
                        self.say(channel, rooms_hash['currScrip'].ref)
                        self.say(channel, "Number of your words = %d " % uwl)
                        self.say(channel, "Number of words in scripture = %d " % swl)
                        
                        self.end_game(channel) 

                gsa.reason = reason_str
                gsa.save()


    def non_turn_based_command(self, channel, nick, command):
        rooms_hash = self.rooms_hash[channel.lower()]        
        repost_mch = re.match('!repost|!redisplay', command, re.IGNORECASE)
        explain_mch = re.match('!explain', command, re.IGNORECASE)
        short_nick = nick.split('!')[0]
        if repost_mch:
            if not rooms_hash['currScrip']:
                self.say(channel, "There is no current scipture to display.")
            else:    
                script_disp = blank_out_letters(self.letters_given, 
                                                str(rooms_hash['currScrip'].verse_text.encode("utf8", "replace")))
                self.say(channel, "The scripture as it currently stands:")
                self.say(channel, SCRIPTURE_COLOUR+script_disp)
                self.say(channel, "Letters currently used are : " + str(self.letters_given))
                self.say(channel, "It is " + self.current_user + "'s turn.")
                if not rooms_hash['solve_state']:
                    self.say(channel, "Waiting for a letter to be chosen.")
                elif rooms_hash['solve_state'] == "yes_no_answer":
                    self.say(channel, "Waiting for a yes/no answer in solving.")
                elif rooms_hash['solve_state'] == "solve_response":
                    self.say(channel, "Waiting for the scripture solution to be type in.")
                    self.say(channel, "CAUTION: Anything you type in chat may be mistaken as a response.")
        elif explain_mch:
            if not rooms_hash['explain']:
                self.say(channel, "Nothing to explain!")
            else:
                self.say(channel, "User Words " + rooms_hash['explain'][0][0])
                self.say(channel, "Scripture Words " + rooms_hash['explain'][0][1])
                if len(rooms_hash['explain']) > 1:
                    for elmt in rooms_hash['explain'][1:]:
                        self.say(channel, elmt[1] + elmt[0] + elmt[2])
                self.say(channel, "End of explanation.")    
                    
    def user_left(self,channel):
        """ Called if a user in game leaves the game """
        rooms_hash = self.rooms_hash[channel.lower()]
        rooms_hash['solve_state'] = None
        if rooms_hash['GameStarted']:
            self._display_scripture(channel)
    

