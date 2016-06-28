from __future__ import absolute_import
from django import forms

class SiteSetupForm(forms.Form):
    consumer_key = forms.CharField(max_length=200)
    consumer_secret = forms.CharField(max_length=200)


class RedditSubmitForm(forms.Form):
    subreddit = forms.ChoiceField()
    title = forms.CharField(max_length=200)
    body = forms.CharField(widget=forms.Textarea, max_length = 1024)
    def __init__(self, *args, **kwargs):
        choices = kwargs.pop('choices')
        super(RedditSubmitForm, self).__init__(*args, **kwargs)
        self.fields['subreddit'].choices = choices 
