# test plugin
from bot.pluginDespatch import Plugin
import re
import datetime
import logging
import requests
from urllib import quote
import json
from logos.roomlib import get_global_option

from django.conf import settings
logger = logging.getLogger(__name__)
logging.config.dictConfig(settings.LOGGING)

def convert_f(celsius):
    return celsius *9/5 + 32

def convert_c(fahrenheit):
    return (fahrenheit - 32)*5/9

def get_weather(loc):
    query = "select * from weather.forecast where woeid in (select woeid from geo.places(1) where text=\"{}\") and u = 'c'".format(loc)
    endpoint = "https://query.yahooapis.com/v1/public/yql?format=json&q="
    url = endpoint + quote(query)
    r = requests.get(url)
    results  = json.loads(r.text)['query']['results']
    return results

def format_weather(results):
    if not results: return "No weather data"
    j = results['channel']
    title = j['item']['title']
    try:
        celsius = int(j['item']['condition']['temp'])
        fahrenheit = convert_f(celsius)
    except ValueError:
        fahrenheit = "*error*"
        celsius = "*error*"
    temperature = "Temp: {} F, {} C.".format(fahrenheit, celsius)
    condition = "Condition: {}.".format(j['item']['condition']['text'])
    try:
        chill_f = int(j['wind']['chill'])
        chill_c = convert_c(chill_f)
    except ValueError:
        chill_f = "*error*"
        chill_c = "*error*"
        
    try:
        kph = int(float(j['wind']['speed']))
        mph = int( kph / 0.621371 )
    except ValueError:
        mph = "*error*"
        kph = "*error*"
    direction = j['wind']['direction']
    wind = "Wind: chill {} F, {} C  Degrees: {} Speed: {} mph, {} kph".format(chill_f, chill_c, direction, mph, kph)
    p = int(float(j['atmosphere']['pressure']))
    lb = int(0.014503773801 * p)
    h = j['atmosphere']['humidity']
    try:
        r = j['atmosphere']['rising']
    except KeyError:
        r = "N/A"
    vk = int(float(j['atmosphere']['visibility']))
    vm = int(vk / 0.621371)
    atmosphere = "Pressure {} mb {} lb/sq in, humidity {}%, rising {}, visibility {} km {} mi.".format(p, lb,  h, r, vk, vm)

    msg = " ".join([title, condition, temperature, wind, atmosphere])
    return msg

def format_forecasts(results):
    j = results['channel']
    title = j['item']['title']
    forecasts = "Forecasts and {}: ".format(title)
    for fc in j['item']['forecast'][:3]:
        day = fc['day']
        hi_c = int(fc['high'])
        lo_c = int(fc['low'])
        hi_f = convert_f(hi_c)
        lo_f = convert_f(lo_c)
        txt = fc['text']
        forecasts += " {} hi: {} C {} F. lo: {} C {} F {}.".format(day, hi_c, hi_f, lo_c, lo_f, txt)

    return forecasts

class WeatherPlugin(Plugin):
    plugin = ("weather", "Weather Plugin")
    def __init__(self, *args, **kwargs):
        Plugin.__init__(self, *args, **kwargs)
        
        self.commands = (\
         (r'w (?P<arg>\S.*)$', self.weather, "Weather query"),
         (r'fc (?P<arg>\S.*)$', self.forecasts, "Weather forecasts"),
        )
    
    def privmsg(self, user, channel, message):
        pass

    def weather(self, regex, chan, nick, **kwargs):
        arg = regex.group('arg')
        results = get_weather(arg)
        str1 = format_weather(results)
        self.say(chan, str1)

    def forecasts(self, regex, chan, nick, **kwargs):
        arg = regex.group('arg')
        results = get_weather(arg)
        str1 = format_forecasts(results)
        self.say(chan, str1)

   
                
            


