#! /usr/bin/env python

from optparse import OptionParser, make_option
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
import logging
import sys
from bs4 import BeautifulSoup
import re
import pytz
from lxml import etree
from datetime import datetime
from cloud_notes.models import Note, Folder

logger = logging.getLogger(__name__)
from django.conf import settings
logger = logging.getLogger(__name__)
logging.config.dictConfig(settings.LOGGING)

class Command(BaseCommand):
    help = 'Import xml notes'

    extra_options = (

        make_option('--xml-file',action='store',
                    help="Path to XML file path"),
        make_option('--user',action='store',
                    help="user to record notes under"),                    
    )
    option_list = BaseCommand.option_list + extra_options


    def handle(self, *args, **options):
        logger.debug ("args = "+str(args))
        logger.debug ("options = "+ str(options))
        

        username = options['user']
        if not username:
            self.stdout.write("You must specify --user <user> ")
            sys.exit(1)
        
        try:
            user = User.objects.get(username = username)
        except User.DoesNotExist:
            self.stdout.write("Not a valid user")
            sys.exit(1)
            
        xml_file = options['xml_file']
        if not xml_file:
            self.stdout.write("You must specify --xml-file=<xml-file>")
            sys.exit(1)
        try:
            f = open(xml_file,"r")
            soup = BeautifulSoup(f, "xml")
            f.close()
            
            self.have_soup(soup, user)
                        
        except IOError:
            self.stdout.write("Could not open xml file: " + repr(xml_file))
        
    def have_soup(self, soup, user):
        main = Folder.objects.get(name="Main")
        tz = pytz.timezone('utc')
        channel = soup.find("channel")
        for item in channel.find_all("item", recursive=False):
            post_type = item.post_type.string    
            if post_type in ('attachment',): continue
            if post_type == "post": 
                
                print item.category['nicename']
                
            if item.encoded.string.strip() == '': continue

            title = item.title.string
            print title
            note = item.encoded.string
            date_str = item.post_date_gmt.string
            if date_str == "0000-00-00 00:00:00":
                date_obj = datetime.utcnow()
            else:
                date_obj = datetime.strptime(item.post_date_gmt.string, '%Y-%m-%d %H:%M:%S')
            # make date object non naive
            # http://stackoverflow.com/questions/13994594/how-to-add-timezone-into-a-naive-datetime-instance-in-python
            date_obj = tz.localize(date_obj)
            print date_obj
            
            obj = Note()
            obj.title = title
            obj.note = note
            obj.post_type = 'note'
            obj.created_at = date_obj
            obj.modified_at = date_obj
            obj.user = user
            obj.folder = main
            obj.save()            
            

