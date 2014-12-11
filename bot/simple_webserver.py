# web interface to nicks list
from twisted.web import server, resource
from twisted.internet import reactor
import cgi
import re
import pdb

from logos.models import GameGames, GameUsers, GameSolveAttempts

class Simple(resource.Resource):
    def game_data(self, request):
        str1 = "<p class=\"scripture=game\">"
        games = GameGames.objects.all()
        for gm in games:
            dt = gm.game_datetime
            ref = gm.ref
            scr = gm.scripture
            try:
                winner = gm.winner
            except GameUsers.DoesNotExist:
                winner = ""
            str1 += "Game :%s<br/>" % (gm.id,)
            str1 += "Date Time: %s<br/>" % (dt,)
            str1 += "Reference: %s<br/>" % (ref,)
            str1 += "Scripture: %s<br/>" % (scr,)
            str1 += "Winner: %s<br/>" % (winner,)
            str1 += "<br/>\n"

        str1 += "</p>"
        return bytes(str1)
    def content_nick_list(self, request):

        try:
            nicks_in_room = self.irc_factory.conn.nicks_db.get_room_nicks(self.room)
        except:
            str1 = "<p class='bot-errors'>The bot is not in room "+self.room+"</p>"
        else:
            nick_build_list = []
            for nick in nicks_in_room:
                if self.irc_factory.conn.nicks_db.get_bot_status(nick):
                    nick_s = "<span class='bot'>" + nick + "</span>"
                else:
                    opstatus = self.irc_factory.conn.nicks_db.get_op_status(nick, self.room)
                    if opstatus == "~":
                        nick_s = "<span class='founder'>" + nick + "</span>"
                    elif opstatus == "&":
                        nick_s = "<span class='sop'>" + nick + "</span>"
                    elif opstatus == "@":
                        nick_s = "<span class='aop'>" + nick + "</span>"
                    elif opstatus == "%":
                        nick_s = "<span class='hop'>" + nick + "</span>"
                    else:
                        nick_s = "<span class='normal'>" + nick + "</span>"
                nick_build_list.append(nick_s)
            str1 = ', '.join(nick_build_list)
            str1 = "<p id='nick-list'>" + str1 + "</p>"
        
        return str1
    
    def render_GET(self, request):
        print request
        print request.args
        print self.irc_factory

        if self.irc_factory:
            if self.irc_factory.conn:
                if 'cssUrl' in request.args:
                    style_url = request.args['cssUrl'].pop()
                    htmlStr = """
<html>
<head>
<link rel="stylesheet" type="text/css" href="%s"> 
</head>
<body></body>
</html>""" % (style_url,)
                elif 'style' in request.args:
                    style = request.args['style'].pop()
                    htmlStr = """
<html>
<head>
</head>
<body style="%s"></body>
</html>""" % (style,)                    
                else:
                    htmlStr = """
<html><head></head>
<body></body>
</html>"""                    
                if 'room' in request.args:
                    self.room = '#' + request.args['room'].pop()
                else:
                    self.room = None
                    
                if request.path == '/nick_list':
                    content = self.content_nick_list(request)
                elif request.path == '/game_data': 
                    content = self.game_data(request)
                else:
                    content = ''
                    
                htmlStr = re.sub('<body([^>]*)></body>', 
                                 r'<body\1>'+content+'</body>',
                                 htmlStr)
                return htmlStr

            else:
                return "<p>Logos not online</p>"
        else:
            return "<p>Bad factory setting</p>"
    def getChild(self, name, request):
            return self

class SimpleWeb():
    def __init__(self, reactor, irc_factory, port):
        simp = Simple()
        simp.irc_factory = irc_factory
        self.site = server.Site(simp)
        reactor.listenTCP(port, self.site)
        
if __name__ == '__main__':
    nw = SimpleWeb(reactor, None)
    reactor.run()