from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.urls import reverse

import re

import logging

from django.conf import settings
logger = logging.getLogger(__name__)
logging.config.dictConfig(settings.LOGGING)

# Create your models here.
class Folder(models.Model):
    name = models.CharField(max_length=30)
    # Folders really need to be specific to User (TO DO)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    def __unicode__(self):
        return u"Folder %d" % (self.id, )

    @staticmethod
    def userChoices(user):
        """ Get folder choices for use with ChooseFolderForm """
        choices = []
        for folder in Folder.objects.filter(user = user):
            choices.append((folder.id, folder.name))
        return choices

class Note(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE)
    title = models.CharField(max_length=120)
    # note_type is something like "memo", "web-page", ... etc
    note_type = models.CharField(blank=True, default="", max_length=15)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField()
    note = models.TextField()

    def get_absolute_url(self): 
        return reverse('cloud_notes.views.preview', args=[self.id])

    @property
    def linecount(self):
        return len(self.note.split('\n'))
        
    @property
    def excerpt(self):
        s = ""
        for ln in self.note.split('\n'):
            if re.match(r'tags', ln, re.I): continue
            s += ln
        return s
        
    def add_tags(self):
        words = re.split(r'\s+', self.note.strip())
        for wrd in words:
            mch = re.match(r'^(#[a-zA-Z0-9-]+)[,.:;]?$', wrd)
            if mch:
                logger.debug( 'tag = ' + wrd )
                tag = mch.group(1)
                obj, created = HashTags.objects.get_or_create(hash_tag__iexact = tag,user = self.user, defaults = {'hash_tag':tag} )
                obj.notes.add(self)

    def __unicode__(self):
        return u"{} \"{}\"...".format(self.id, self.title[0:10])
        
        
class HashTags(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    hash_tag = models.CharField(max_length=30, db_index = True)
    created_at = models.DateTimeField(auto_now_add = True)
    notes = models.ManyToManyField(Note)

    def __unicode__(self):
        return u"%s" % (self.hash_tag, )


@receiver(post_save, sender=Note)
def note_post_save_handler(sender, instance, created, **kwargs):
    for tag in HashTags.objects.filter(user = instance.user):
        tag.notes.remove(instance)
        if tag.notes.count() == 0:
            tag.delete()
    instance.add_tags()
    
@receiver(post_save, sender=User)
def new_user_handler(sender, instance, created, **kwargs):
    if created:
        user = instance
        print ("creating main notes folder for "+user.username)
        main = Folder(name="Main", user=user)
        main.save()
        trash = Folder(name="Trash", user=user)
        trash.save()
        
