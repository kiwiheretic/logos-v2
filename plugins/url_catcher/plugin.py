# test plugin
from bot.pluginDespatch import Plugin
import re
import datetime
import logging
from models import CapturedUrls

from logos.settings import LOGGING
logger = logging.getLogger(__name__)
logging.config.dictConfig(LOGGING)

class UrlCatcherPlugin(Plugin):
    plugin = ("url_catcher", "Url Catcher Module")
    def __init__(self, *args, **kwargs):
        Plugin.__init__(self, *args, **kwargs)
        self.urls = []
        
        self.commands = (\
         (r'urls\s+(?P<room>#[a-zA-z0-9-]+)\s+(?P<count>\d+)', self.urls_display, "display a list of captured urls"),
         (r'urls\s+(?P<room>#[a-zA-z0-9-]+)$', self.urls_display, "display a list of captured urls"),
        )
    
    def urls_display(self, regex, chan, nick, **kwargs):
        if 'count' in regex.groupdict():
            num_to_print = int(regex.group('count'))
        else:
            # default to 5 if no number specified
            num_to_print = 5
        # send the urls in order of reverse chronological
        # order
        cap_urls = CapturedUrls.objects.filter(room=chan.lower()).\
            order_by('-timestamp')[:num_to_print]
        for url in cap_urls:
            timestamp = str(url.timestamp)
            self.notice(nick, "{} {} -- {}".format(timestamp, url.nick, url.url))

    def privmsg(self, user, channel, message):
        # Capture any matching urls and keep it in buffer
        url_mch = re.search('(?:https?://\S+)|www\.\S+', message, re.I)
        if url_mch:
            url = url_mch.group(0)
            logger.info("capturing url : " + url)
            timestamp = datetime.datetime.utcnow()
            cap_url = CapturedUrls(timestamp=timestamp, nick=user, 
                                   room=channel.lower(), 
                                   url=url) 
            cap_url.save()


            

   
                
            


