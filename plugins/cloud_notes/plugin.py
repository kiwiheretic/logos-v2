# test plugin
from bot.pluginDespatch import Plugin
import re
from datetime import datetime
import pytz
from django.contrib.auth.models import User

import logging
from logos.settings import LOGGING
logger = logging.getLogger(__name__)
logging.config.dictConfig(LOGGING)

from cloud_notes.models import Note, Folder
from bot.logos_decorators import login_required

READ_SIZE = 250
# If using this file as a starting point for your plugin
# then remember to change the class name 'MyBotPlugin' to
# something more meaningful.
class NotesPlugin(Plugin):
    # Uncomment the line below to load this plugin.  Also if
    # you are using this as a starting point for your own plugin
    # remember to change 'sample' to be a unique identifier for your plugin,
    # and 'My Bot Plugin' to a short description for your plugin.
    plugin = ('notes', 'Cloud Notes')
    
    def __init__(self, *args, **kwargs):
        Plugin.__init__(self, *args, **kwargs)
        self.commands = ((r'list$', self.list_notes, 'list all notes'),
                         (r'list (?P<range>\d*-\d*)', self.list_notes, 'list all notes'),
                         (r'read (?P<note_id>\d+)', self.read, 'read a note'),
                         (r'read more', self.read_more, 'more reading of note'),
                         (r'notes on$', self.start_logging, 'start logging bible notes'),
                         (r'notes off$', self.stop_logging, 'start logging bible notes'),
                         )
        self.user_notes = {}

    def _in_usernotes(self, username, key):
        if username in self.user_notes:
            if key in self.user_notes[username]:
                return True
            else:
                return False
        else:
            return False
        
    def _update_usernotes_hash(self, username, dict_values):
        if username not in self.user_notes:
            self.user_notes[username] = dict_values
        else:
            for k, v in dict_values.iteritems():
                self.user_notes[username][k] = v

    def privmsg(self, user, channel, message):
        
        nick,_ = user.split('!')
        username = self.get_auth().get_username(nick)
        if username and username in self.user_notes:
            regex = re.match("#(.*)",message)
            if regex :
                text = regex.group(1)
                logger.debug("note_users = " + str(self.user_notes))
                note = self.user_notes[username]['note']
                note.note += "\n" + text + "\n"
                dt = datetime.utcnow()
                utc_tz = pytz.timezone("UTC")                
                note.modified_at = utc_tz.localize(dt)
                note.save()
                self.notice(nick, "-- text logged to cloud notes --")

    def onSignal_verse_lookup(self, source, data):
        nick = data['nick']
        chan = data['chan']
        username = self.get_auth().get_username(nick)
        if username and username in self.user_notes:
            note = self.user_notes[username]['note']
            for verse in data['verses']:
                verse_txt = " ".join(verse) + "\n"
                note.note += verse_txt
            dt = datetime.utcnow()
            utc_tz = pytz.timezone("UTC")                
            note.modified_at = utc_tz.localize(dt)
            note.save()
            self.notice(nick, "-- verse(s) logged to cloud notes --")

    def onSignal_verse_search(self, source, data):
        nick = data['nick']
        chan = data['chan']
        username = self.get_auth().get_username(nick)
        if username and username in self.user_notes:
            note = self.user_notes[username]['note']
            note.note += "\n"
            for verse_txt in data['verses']:
                note.note += verse_txt + "\n"
            dt = datetime.utcnow()
            utc_tz = pytz.timezone("UTC")                
            note.modified_at = utc_tz.localize(dt)
            note.save()
            self.notice(nick, "-- verses searched logged to cloud notes --")

    def onSignal_logout(self, source, data):
        username = data['username']
        logger.debug("cloud notes: onSignal_logout " + repr(username))
        logger.debug("cloud notes: self.user_notes " + repr(self.user_notes))
        if username in self.user_notes:
            del self.user_notes[username]
                
    @login_required()
    def start_logging(self, regex, chan, nick, **kwargs):
        username = self.get_auth().get_username(nick)
        user = User.objects.get(username = username)
        
        post_title = "Logos Notes " + datetime.now().strftime('%d-%b-%Y')
        dt = datetime.utcnow()
        utc_tz = pytz.timezone("UTC")
        try:
            note = Note.objects.get(title = post_title)
            
        except Note.DoesNotExist:
            main = Folder.objects.get(name="Main")
            
            
            note = Note(title = post_title,
                        folder = main,
                        user = user,
                        created_at = utc_tz.localize(dt),
                        modified_at = utc_tz.localize(dt),
                        note_type = "bible note",
                        note = "Bible Note: \n")
            note.save()
        self._update_usernotes_hash(username, {'note':note})
        self.say(chan, "Note logging turned on for "+nick)

    @login_required()
    def stop_logging(self, regex, chan, nick, **kwargs):
        username = self.get_auth().get_username(nick)
        if username in self.user_notes:
            del self.user_notes[username]['note']
        self.say(chan, "Note logging turned off for "+nick)    


    
    @login_required()
    def list_notes(self, regex, chan, nick, **kwargs):
        logger.debug("list_notes: " + str(self.user_notes))
        num_to_list = 4
        username = self.get_auth().get_username(nick)
        notes = None
        if 'range' in regex.groupdict():
            range = regex.group('range')
            mch1 = re.match(r'-(\d+)$', range) 
            mch2 = re.match(r'(\d+)-$', range)
            mch3 = re.match(r'(\d+)-(\d+)$', range) 
            mch4 = re.match(r'-$', range) 
            if mch1:
                lidx = int(mch1.group(1))
                notes = Note.objects.\
                    filter(user__username = nick.lower(), pk__lte = lidx).\
                    exclude(folder__name = 'Trash').\
                    order_by('-id')[:num_to_list]
                fidx = notes[len(notes)-1].id
                self._update_usernotes_hash(username, {'list_index':fidx-1})
            elif mch2:
                fidx = int(mch2.group(1))
                notes = Note.objects.\
                    filter(user__username = nick.lower(), pk__gte = fidx).\
                    exclude(folder__name = 'Trash').\
                    order_by('id')[:num_to_list]
                idx = notes[0].id
                notes = reversed(notes)
                self._update_usernotes_hash(username, {'list_index':idx-1})
            elif mch3:
                fidx = int(mch3.group(1))
                lidx = int(mch3.group(2))
                notes = Note.objects.\
                    filter(user__username = nick.lower(), pk__gte = fidx, \
                           pk__lte = lidx).\
                    exclude(folder__name = 'Trash').\
                    order_by('-id')[:num_to_list]                
                self._update_usernotes_hash(username, {'list_index':fidx-1})
            elif mch4:
                if self._in_usernotes(username, 'list_index'):
                    idx = self.user_notes[username]['list_index']
                    logger.debug( "cloud_notes: idx = " + str(idx))
                    notes = Note.objects.\
                        filter(user__username = nick.lower(), pk__lte = idx).\
                        exclude(folder__name = 'Trash').\
                        order_by('-id')[:num_to_list]
                    if notes: #if any found
                        idx = notes[len(notes)-1].id
                        self.user_notes[username]['list_index'] = idx-1
                    else:
                        self.say(chan, "**No more notes found***")
        else:
            notes = Note.objects.filter(user__username = nick.lower()).\
                exclude(folder__name = 'Trash').order_by('-id')[:num_to_list]
            lidx = notes[len(notes)-1].id
            self._update_usernotes_hash(username, {'list_index':lidx-1})
                            
        if notes:
            for note in notes:
                self.say(chan, str(note.id) + " " + note.title)

    @login_required()
    def read_more(self, regex, chan, nick, **kwargs):
        logger.debug("read more: " + str(self.user_notes))
        username = self.get_auth().get_username(nick)
        if username not in self.user_notes:
            self.say(chan, "Nothing to read")
        else:
            if 'reading' in self.user_notes[username]:
                reading = self.user_notes[username]['reading'].note
                ridx = self.user_notes[username]['ridx']
                try:
                    ridx2 = reading.rindex(" ", ridx, ridx+READ_SIZE)                
                    notestr = reading[ridx:ridx2].replace("\n", " ").strip()
                    self.user_notes[username]['ridx'] = ridx2
                    if notestr != "":
                        self.say(chan, notestr)
                    else:
                        self.say(chan, "**Note End**")

                except ValueError:
                    self.say(chan, "**Note End**")
            else:
                self.say(chan, "Nothing to read")

    @login_required()
    def read(self, regex, chan, nick, **kwargs):
        logger.debug("read: " + str(self.user_notes))
        note_id = regex.group('note_id')
        username = self.get_auth().get_username(nick)
        try:
            note = Note.objects.get(pk=note_id)
            notestr = re.sub(r'\n', ' ', note.note)
            ridx = notestr.rindex(" ", 0, READ_SIZE)
            self._update_usernotes_hash(username, {'reading':note, 'ridx':ridx})

            self.say(chan, notestr[0:ridx])
        except Note.DoesNotExist:
            self.notice(nick, "Note does not exist")
        

