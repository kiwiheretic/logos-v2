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

from cloud_memos.models import Memo, Folder
from bot.logos_decorators import login_required

READ_SIZE = 250
class MemosPlugin(Plugin):
    plugin = ('memos', 'Cloud Memos')
    
    def __init__(self, *args, **kwargs):
        # Plugin.__init__(self, *args, **kwargs)
        super(MemosPlugin, self).__init__(*args, **kwargs)

        self.commands = ((r'list$', self.list_memos, 'list all memos'),
                         (r'list new$', self.list_new_memos, 'list new memos'),
                         (r'send (?P<recipient>\S+) (?P<message>.*)$', self.send_memo, 'send new memos'),
                         (r'check$', self.check, 'check for unread memos'),
                         (r'read (?P<memo_id>\d+)', self.read, 'read a memo'),
                         (r'folders', self.list_folders, 'List memo folders'),
                         )
        # self.user_memos = {}

    def update_user_memo_info(self, user=None, folder=None, memos = None):
        if not user: return
        userl = user.lower()
        if userl not in self.user_memos:
            self.user_memos[userl] = {}
        if folder:
            self.user_memos[userl].update({'folder':folder})
        else:
            self.user_memos[userl].update({'folder':'inbox'})
        
        if memos:
            self.user_memos[userl].update({'memos':memos}) 
            
    def onSignal_login(self, source, data):
        nick = data['nick']
        
        # check for unread memos
        self._check(nick)
    
    def onSignal_logout(self, source, data):
        username = data['username']
        logger.debug("cloud memos: onSignal_logout " + repr(username))
        # del self.user_memos[username.lower()]       
    
    def _get_memos_obj(self, nick, folder_name='inbox', new=False):
        username = self.get_auth().get_username(nick)
        user = User.objects.get(username = username)
        if new:
            memos = Memo.objects.filter(folder__name=folder_name, 
                to_user__username = nick.lower(),
                viewed_on__isnull = True).order_by('-id')
        else:
            memos = Memo.objects.filter(folder__name=folder_name, 
                to_user__username = nick.lower()).order_by('-id')
        return memos
    
    def _check(self, nick):
        """  check for unread memos """

        username = self.get_auth().get_username(nick)
        user = User.objects.get(username=username)
        unread_memos = Memo.objects.filter(folder__name='inbox', 
            to_user = user, viewed_on__isnull = True).count()
        if unread_memos > 0:
            self.notice(nick,'You have %d unread memos!' % (unread_memos,))
    
    @login_required()
    def check(self, regex, chan, nick, **kwargs):
        """  check for unread memos """
        self._check(nick)
        
            
    @login_required()
    def list_folders(self, regex, chan, nick, **kwargs):
        username = self.get_auth().get_username(nick)
        user = User.objects.get(username = username)
        for folder in Folder.objects.filter(user=user):
            self.notice(nick, str(folder.id)+" " +folder.name)
        self.notice(nick,'--end of list--')
    
    @login_required()
    def sel_folder(self, regex, chan, nick, **kwargs):
        username = self.get_auth().get_username(nick)
        user = User.objects.get(username = username)
        try:
            folder = Folder.objects.get(pk=regex.group('folder_id'),
                                        user = user)
            self._update_usernotes_hash(username, {'folder':folder})
            self.notice(nick, "--Folder successfully opened--")
        except Folder.DoesNotExist:
            self.notice(nick, "--Folder does not exist--")

    @login_required()
    def send_memo(self, regex, chan, nick, **kwargs):
        print ("Send Memo ...")
        recipient = regex.group('recipient')
        message = regex.group('message')
        username = self.get_auth().get_username(nick)
        user = User.objects.get(username = username)
        try:
            recip = User.objects.get(username = recipient)
        except User.DoesNotExist:
            self.notice(nick, "I do not know this user")
            return
        Memo.send_memo(user, recip, "Memo", message)
        self.notice(nick, "Memo sent")
        
    @login_required()
    def list_memos(self, regex, chan, nick, **kwargs):
        num_to_list = 10
        memos = self._get_memos_obj(nick)
                        
        if memos:
            for idx, memo in enumerate(memos):
                self.notice(nick, str(idx) + " " + memo.from_user.username + " " + memo.subject)
                if idx >= num_to_list: break
                
        else:
            self.notice(nick, '** No memos found **')


    @login_required()
    def list_new_memos(self, regex, chan, nick, **kwargs):
        num_to_list = 10
        memos = self._get_memos_obj(nick, new=True)
                        
        if memos:
            for idx, memo in enumerate(memos):
                self.notice(nick, str(idx) + " " + memo.from_user.username + " " + memo.subject)
                if idx >= num_to_list: break
                
        else:
            self.notice(nick, '** No memos found **')


    @login_required()
    def read(self, regex, chan, nick, **kwargs):
        logger.debug("read memos: %s %s " % (chan, nick))
        memos = self._get_memos_obj(nick)
        memo_id = int(regex.group('memo_id'))
        try:
            memo = memos[memo_id]
            text = re.sub(r'\n', ' ', memo.text)
            self.notice(nick, text)
        except IndexError:
            self.notice(nick, "Memo not in list")

        

