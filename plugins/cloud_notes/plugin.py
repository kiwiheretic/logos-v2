# test plugin
from bot.pluginDespatch import Plugin
import re
import logging
from logos.settings import LOGGING
logger = logging.getLogger(__name__)
logging.config.dictConfig(LOGGING)

from cloud_notes.models import Note
from bot.logos_decorators import login_required

# If using this file as a starting point for your plugin
# then remember to change the class name 'MyBotPlugin' to
# something more meaningful.
class MyBotPlugin(Plugin):
    # Uncomment the line below to load this plugin.  Also if
    # you are using this as a starting point for your own plugin
    # remember to change 'sample' to be a unique identifier for your plugin,
    # and 'My Bot Plugin' to a short description for your plugin.
    plugin = ('cloud', 'Cloud Plugin')
    
    def __init__(self, *args, **kwargs):
        Plugin.__init__(self, *args, **kwargs)
        self.commands = ((r'list$', self.list_memos, 'list all memos'),
                         (r'list (?P<range>\d*-\d*)', self.list_memos, 'list all memos'),
                         (r'read (?P<memo_id>\d+)', self.read, 'read a memo'),

                         )
        self.conversation = []
    
    @login_required()
    def list_memos(self, regex, chan, nick, **kwargs):
#        import pdb; pdb.set_trace()
        num_to_list = 4
        if 'range' in regex.groupdict():
            range = regex.group('range')
            mch1 = re.match(r'-(\d+)$', range) 
            mch2 = re.match(r'(\d+)-$', range)
            mch3 = re.match(r'(\d+)-(\d+)$', range) 
            if mch1:
                lidx = int(mch1.group(1))
                notes = Note.objects.\
                    filter(user__username = nick.lower(), pk__lte = lidx).\
                    exclude(folder__name = 'Trash').\
                    order_by('-id')[:num_to_list]
            elif mch2:
                fidx = int(mch2.group(1))
                notes = Note.objects.\
                    filter(user__username = nick.lower(), pk__gte = fidx).\
                    exclude(folder__name = 'Trash').\
                    order_by('id')[:num_to_list]
                notes = reversed(notes)
            elif mch3:
                fidx = int(mch3.group(1))
                lidx = int(mch3.group(2))
                notes = Note.objects.\
                    filter(user__username = nick.lower(), pk__gte = fidx, \
                           pk__lte = lidx).\
                    exclude(folder__name = 'Trash').\
                    order_by('-id')[:num_to_list]                
        else:
            notes = Note.objects.filter(user__username = nick.lower()).\
                exclude(folder__name = 'Trash').order_by('-id')[:num_to_list]
        for note in notes:
            self.say(chan, str(note.id) + " " + note.title)

    def read(self, regex, chan, nick, **kwargs):
        memo_id = regex.group('memo_id')
        try:
            note = Note.objects.get(pk=memo_id)
            notestr = re.sub(r'\n', ' ', note.note[:800])
            self.say(chan, notestr)
        except Note.DoesNotExist:
            self.notice(nick, "Memo does not exist")
        

