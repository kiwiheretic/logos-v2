# test plugin
from bot.pluginDespatch import Plugin
import re
import pdb
import logging
from logos.settings import LOGGING
logger = logging.getLogger(__name__)
logging.config.dictConfig(LOGGING)

class UrlCatcherPlugin(Plugin):
    plugin = ("url_catcher", "Url Catcher Module")
    def __init__(self, *args, **kwargs):
        Plugin.__init__(self, *args, **kwargs)
        self.urls = []
        
        self.commands = (\
         (r'urls\s+(\d+)|urls', self.urls_display, "display a list of captured urls"),
        )
    
    def urls_display(self, regex, chan, nick, **kwargs):
        if regex.lastindex == 1:
            num_to_print = int(regex.group(1))
        else:
            # default to 5 if no number specified
            num_to_print = 5
        # send the urls in order of reverse chronological
        # order
        for url in reversed(self.urls[:num_to_print]):
            self.notice(nick, url)

    def privmsg(self, user, channel, message):
        # Capture any matching urls and keep it in buffer
        url_mch = re.match('(?:https?://\S+)|www\.\S+', message, re.I)
        if url_mch:
            logger.info("capturing url : " + url_mch.group(0))
            self.urls.append(url_mch.group(0))
            # keep only the last 20 items in the list
            self.urls = self.urls[-20:]


            

   
                
            


