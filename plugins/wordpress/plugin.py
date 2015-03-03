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
                         (r'purge$', self.purge, 'purge all posts'),
                         (r'start\s+logging$', self.start_logging,
                          'Log all text to wordpress post'),
                         )
        self.wp_users = {}
        self.problem_usernames = []
    
    def privmsg(self, user, channel, message):
        for user in self.wp_users.keys():
            pass
    
    def on_activate(self):
        """ When this plugin is activated for the network or startup
        occurs. """
        pass
    
            
    def onSignal_login(self, source, data):
        print "login,",repr(data)
        nick = data['nick']
        
        username = self.get_auth().get_username(nick)

        self.wp_users[username] = {'nick':nick, 'user':data['user']}
        # get WP login if there is one
        try:
            wp = WPCredentials.objects.get(user=data['user'])
            self.wp_users[username]['wpdb'] = wp
            if USE_THREADS:
                self.reactor.callInThread(self._wp_init, username)
            else:
                self._wp_init(username)                
        except WPCredentials.DoesNotExist:
            pass
        
    def _wp_init(self, username):
        
        wpdb = self.wp_users[username]['wpdb']
        wp_title = "Notes " + datetime.now().strftime('%d-%b-%Y')
        try:
            wp = Client(wpdb.url + "/xmlrpc.php", 'splat', 'qw3rty123')
            
            post_chunks = 20
            offset = 0
            the_post = None
            posts = wp.call(GetPosts({'number':post_chunks}))
            while posts:
                offset += post_chunks
                for post in posts:
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
    """ This is an automatically generated post courtesy of the Wordpress plugin
    for Logos-v2 IRC bot courtesy of SplatsCreations.
    Please see the website: http://github.com/kiwiheretic/logos-v2 for more 
    information.
    
    """
                the_post.id = wp.call(NewPost(the_post))
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
        for username in self.problem_usernames:
            nick = self.wp_users[username]['nick']
            self.notice(nick, "Trying your WP account again")
            if USE_THREADS:
                self.reactor.callInThread(self._wp_init, username)
            else:
                self._wp_init(username)    
        
    def onSignal_logout(self, source, data):
        print "logout ", data
        username = self.get_auth().get_username(nick)
        if username in self.wp_users:
            del self.wp_users[username]
        
    def onSignal_verse_lookup(self, source, data):
        nick = data['nick']
        username = self.get_auth().get_username(nick)
        if username and 'wp' in self.wp_users[username]:
            wp = self.wp_users[username]['wp']
            if 'post' in self.wp_users[username]:
                the_post = self.wp_users[username]['post']
                for verse in data['verses']:
                    verse_txt = " ".join(verse) + "\n"
                    the_post.content += verse_txt
                wp.call(EditPost(the_post.id, the_post))
                    
    def onSignal_verse_search(self, source, data):
        nick = data['nick']
        username = self.get_auth().get_username(nick)
        if username and 'wp' in self.wp_users[username]:
            wp = self.wp_users[username]['wp']
            if 'post' in self.wp_users[username]:
                the_post = self.wp_users[username]['post']
                for verse_txt in data['verses']:
                    the_post.content += verse_txt + "\n"
                wp.call(EditPost(the_post.id, the_post))
                
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
            
    
    def purge(self, regex, chan, nick, **kwargs):
        for username in self.wp_users.keys():
            print username
    
    @login_required()
    def start_logging(self, regex, chan, nick, **kwargs):
        wp_title = "Notes " + datetime.now().strftime('%d-%b-%Y')
        if nick.lower() in self.wp_users:
            username = self.get_auth().get_username(nick)
            wpdb = self.wp_users[username]['wpdb']
            wp = Client(wpdb.url + "/xmlrpc.php", 'splat', 'qw3rty123')
            
            offset = 0
            the_post = None
            posts = wp.call(GetPosts({'number':20}))
            while posts:
                offset += 20
                for post in posts:
                    print post.title
                    if post.title == wp_title:
                        the_post = post
                        break

    #                print type(post.content)
    #                print post.content.encode("cp1252")            
                if the_post: break
                posts = wp.call(GetPosts({'number':20, 'offset':offset}))
            if not the_post:
                post = WordPressPost()
                post.title = wp_title
                post.content = 'This is an automatically generated header.'
                post.id = wp.call(NewPost(post))
        else:
            self.say(chan, "You haven't registered your wordpress url yet")
        
        