# test plugin
from bot.pluginDespatch import Plugin
import re
import datetime
import logging
import pyowm
from logos.roomlib import get_global_option

from django.conf import settings
logger = logging.getLogger(__name__)
logging.config.dictConfig(settings.LOGGING)

class WeatherPlugin(Plugin):
    plugin = ("weather", "Weather Plugin")
    def __init__(self, *args, **kwargs):
        Plugin.__init__(self, *args, **kwargs)
        
        self.commands = (\
         (r'w (?P<arg>\S.*)$', self.weather, "Weather query"),
        )
    
    def privmsg(self, user, channel, message):
        pass

    def weather(self, regex, chan, nick, **kwargs):
        api_key = get_global_option('weather_api_key')
        owm = pyowm.OWM(api_key)
        arg = regex.group('arg')
        observation = owm.weather_at_place(arg)
        w = observation.get_weather()
        tm = w.get_reference_time()
        tm_str = datetime.datetime.fromtimestamp(tm).strftime("%b %d %Y %H:%M")
        str1 = "Reference time : " + tm_str
        str1 += " Status : {}. ".format(w.get_status())
        str1 += " Wind: speed {speed} ".format(**w.get_wind())
        str1 += " Humidity: {}.".format(w.get_humidity())
        celsius = w.get_temperature('celsius')['temp']
        fahrenheit = w.get_temperature('fahrenheit')['temp']
        str1 += " Temperature {} F {} C".format(celsius, fahrenheit)
#        str1 += " Temperature (F): {temp_min}, {temp}, {temp_max}.".format(**w.get_temperature())
#        str1 += " Temperature (C): {temp_min}, {temp}, {temp_max}.".format(**w.get_temperature('celsius'))
        self.say(chan, str1)


            

   
                
            


