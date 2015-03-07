# python test wordpress
USE_THREADS = True
# dependencies...
# pip install python-wordpress-xmlrpc
from bot.logos_decorators import login_required
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import GetPosts, NewPost, EditPost
from models import WPCredentials
from bot.pluginDespatch import Plugin
from datetime import datetime
import socket
import copy
import re
from django.contrib.auth.models import User

import logging
from django.conf import settings
logger = logging.getLogger(__name__)
logging.config.dictConfig(settings.LOGGING)

# Time to try the WP connection again, needs to be greater than the socket timeout
# specified in IRC.py
TRY_AGAIN_TIME = 120

class WordpressPlugin(Plugin):
    
    plugin = ('wordpress', 'Wordpress')
        
    def __init__(self, *args, **kwargs):
        super(WordpressPlugin, self).__init__(*args, **kwargs)
        self.commands = (\
                         (r'set\s+wordpress\s+account\s+(?P<url>\S+)\s+(?P<username>[a-zA-z0-9-]+)\s+(?P<password>\S+)', 
                          self.set_wordpress_account, 
                          'Set the wordpress account to use'),
                         (r'get\s+wordpress\s+account$', 
                          self.get_wordpress_account, "Retrieve wordpress account details"),
                         (r'start\s+logging$', self.start_logging,
                          'Log all text to wordpress post'),
                         (r'stop\s+logging$', self.stop_logging,
                          'Stop logging text to wordpress post'),                          
                         )
        self.wp_users = {}
        self.problem_usernames = []
    
    def privmsg(self, user, channel, message):
        nick,_ = user.split('!')
        username = self.get_auth().get_username(nick)
        if username and username in self.wp_users:
            if self.wp_users[username]['logging']:
                regex = re.match("#(.*)",message)
                if regex :
                    text = regex.group(1)
                    logger.debug("wp_users = " + str(self.wp_users))
                    wp = self.wp_users[username]['wp']
                    the_post = self.wp_users[username]['post']
                    the_post.content += "\n" + text + "\n"
                    wp.call(EditPost(the_post.id, the_post))
                    self.notice(nick, "-- text logged to WP --")

    
    def on_activate(self):
        """ When this plugin is activated for the network or startup
        occurs. """
        pass
    
            
    def onSignal_login(self, source, data):
        print "login,",repr(data)
        nick = data['nick']
        
        username = self.get_auth().get_username(nick)

        self.wp_users[username] = {'nick':nick, 'user':data['user'], 
                                   'logging':False, 'wpdb':None}
        # get WP login if there is one
        
        
    def _get_post(self, wp):
        wp_title = "Logos Notes " + datetime.now().strftime('%d-%b-%Y')
        post_chunks = 20
        offset = 0
        the_post = None
        posts = wp.call(GetPosts({'number':post_chunks}))
        while posts:
            offset += post_chunks
            for post in posts:
#                    print post.title
#                    print post.post_status
                if post.title == wp_title:
                    the_post = post
                    break
            if the_post: break
            if len(posts) < post_chunks: break
            posts = wp.call(GetPosts({'number':post_chunks, 'offset':offset}))
        if not the_post:
            the_post = WordPressPost()
            the_post.title = wp_title
            the_post.content = \
    "This is an automatically generated post courtesy of the Wordpress " + \
    "plugin for Logos-v2 IRC by SplatsCreations.  " + \
    "Please see the website: http://github.com/kiwiheretic/logos-v2 for more " + \
    "information.<br/>\n"
            the_post.id = wp.call(NewPost(the_post))
        else:
            print "Existing Post found"
        return the_post
    
                
    def _wp_init(self, username):
        logger.debug( "_wp_init")
        wpdb = self.wp_users[username]['wpdb']
        
        try:
            wp = Client(wpdb.url + "/xmlrpc.php", 'splat', 'qw3rty123')
            the_post = self._get_post(wp)
            self.wp_users[username]['wp'] = wp
            self.wp_users[username]['post'] = the_post
            print self.wp_users
        except socket.timeout:
            self.reactor.callFromThread(self._on_socket_error, username)

    
    def _on_socket_error(self, username):
        print "WP: an error occurred with "+username
        self.problem_usernames.append(username)
        nick = self.wp_users[username]['nick']
        self.notice(nick, "There was a problem with your WP account, will try again shortly...")
        self.reactor.callLater(TRY_AGAIN_TIME, self._try_again)

    def _try_again(self):
        for username in copy.copy(self.problem_usernames):
            self.problem_usernames.remove(username)
            nick = self.wp_users[username]['nick']
            self.notice(nick, "Trying your WP account again")
            if USE_THREADS:
                self.reactor.callInThread(self._wp_init, username)
            else:
                self._wp_init(username)    
        
    def onSignal_logout(self, source, data):
        print "logout ", data
        username = data['username']
        if username in self.wp_users:
            del self.wp_users[username]
        
    def onSignal_verse_lookup(self, source, data):
        nick = data['nick']
        username = self.get_auth().get_username(nick)
        if username and 'wp' in self.wp_users[username] and \
            self.wp_users[username]['logging']:

            wp = self.wp_users[username]['wp']
            if 'post' in self.wp_users[username]:
                the_post = self.wp_users[username]['post']
                for verse in data['verses']:
                    verse_txt = " ".join(verse) + "\n"
                    the_post.content += verse_txt
                wp.call(EditPost(the_post.id, the_post))
                self.notice(nick, "-- verse(s) logged to WP --")
                    
    def onSignal_verse_search(self, source, data):
        nick = data['nick']
        username = self.get_auth().get_username(nick)
        if username and 'wp' in self.wp_users[username] and \
            self.wp_users[username]['logging']:
                        
            wp = self.wp_users[username]['wp']
            if 'post' in self.wp_users[username]:
                the_post = self.wp_users[username]['post']
                the_post.content += "<br/>\n"
                for verse_txt in data['verses']:
                    the_post.content += verse_txt + "\n"
                wp.call(EditPost(the_post.id, the_post))
                self.notice(nick, "-- verses searched logged to WP --")

                
    @login_required()
    def set_wordpress_account(self, regex, chan, nick, **kwargs):
        url = regex.group('url')
        username = regex.group('username')
        password = regex.group('password')
        user = self.get_auth().get_user_obj(nick)
        defs = {'url': url, 'username':username, 'password':password}
        obj, created = WPCredentials.objects.update_or_create (defaults = defs,
                                                               user = user)
        if created:
            self.wp_users[nick.lower()] = {"user":user, "wpdb":obj}
        self.say(chan, "WP Credentials saved")
  
    @login_required()
    def get_wordpress_account(self, regex, chan, nick, **kwargs):
        username = self.get_auth().get_username(nick)
        user = User.objects.get(username=username)
        wpcred = user.wpcredentials_set.first()
        self.notice(nick, "WP Credentials")
        self.notice(nick, "Url = {}, username = {}, password = {}".\
                    format(wpcred.url,wpcred.username,wpcred.password))
    
    @login_required()
    def start_logging(self, regex, chan, nick, **kwargs):
        username = self.get_auth().get_username(nick)
        try:
            wp = WPCredentials.objects.get(user__username=username)
            self.wp_users[username]['wpdb'] = wp
#            if USE_THREADS:
#                self.reactor.callInThread(self._wp_init, username)
#            else:
#                self._wp_init(username)                

            if username and username in self.wp_users:
                if not self.wp_users[username]['logging']:
                    if USE_THREADS:
                        self.reactor.callInThread(self._wp_init, username)
                    else:
                        self._wp_init(username)                
                self.wp_users[username]['logging'] = True
                self.notice(nick, "WP Logging turned on")

        except WPCredentials.DoesNotExist:
            self.notice(nick, "Your wordpress credentials were not found")        

                
        
    @login_required()
    def stop_logging(self, regex, chan, nick, **kwargs):
        username = self.get_auth().get_username(nick)
        if username and username in self.wp_users:
            self.wp_users[username]['logging'] = False
            self.notice(nick, "WP Logging turned off")
