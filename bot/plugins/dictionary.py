from HTMLParser import HTMLParser
import urllib2
import re
import sys
from bot.pluginDespatch import Plugin
import pdb

def find_attr_value(attrs, attr):
    for pr in attrs:
        if pr[0] == attr:
            return pr[1]
    return None


class DictHTMLParser(HTMLParser):
    def __init__(self, num_entries_to_retrieve):
        self.dndata_found = False
        self.result = ''
        self.index = 1
        self.num_entries = num_entries_to_retrieve
        self.str = ''
        HTMLParser.__init__(self)
        
    def handle_starttag(self, tag, attrs):
        if self.index > self.num_entries: return
    
        if tag=="td": 
            value = find_attr_value(attrs, 'class')
            if value == 'td3n2':
                self.dndata_found = True
                self.str = str(self.index) + '. '
#                print "Encountered a start tag:", tag, value
    def handle_endtag(self, tag):
        if self.index > self.num_entries: return
        if tag == 'td' and self.dndata_found:
            self.index += 1
            self.result += self.str
#            print self.str
        self.dndata_found = False
        self.str = ''
#        print "Encountered an end tag :", tag
    def handle_data(self, data):
        if self.index > self.num_entries: return
        if self.dndata_found:
            self.str += data.strip() + ' '

class DictionaryPlugin(Plugin):
    def command(self, nick, user, chan, orig_msg, msg, act):
        dict_mch = re.match('d\s+([^\s]+)$', msg)
        if dict_mch:
            word = dict_mch.group(1)
            url = 'http://dictionary.reference.com/browse/%s' % (word,)
            data  = urllib2.urlopen(url)

            html_stripped = (re.subn(r'<(script).*?</\1>(?s)', '', data.read())[0])
            html_stripped = (re.subn(r'<(style).*?</\1>(?s)', '', html_stripped)[0])

            html_stripped = html_stripped.decode("utf-8")
            html_stripped = html_stripped.encode("ascii","replace")

            f = open('html_stripped.html','w')
            f.write(html_stripped)
            f.close()            

            parser = DictHTMLParser(10)
            found = False
            for ln in html_stripped.split('\n'):
                if 'World English Dictionary' in ln: 
                    found = True
                    idx = 0
                if found: 
                    parser.feed(ln)               
                    idx += 1
                    if idx > 30 : 
                        break

            s = str(parser.result.strip())
            if s == '':
                s = 'Could not find word "%s" in dictionary' % (wrd,)
            self.say(chan, s)
            
