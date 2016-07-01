from __future__ import absolute_import
from django import forms
from django.utils.translation import ugettext as _

class SiteSetupForm(forms.Form):
    consumer_key = forms.CharField(max_length=200)
    consumer_secret = forms.CharField(max_length=200)


class RedditSubmitForm(forms.Form):
    subreddit = forms.ChoiceField()
    title = forms.CharField(max_length=200)
    url = forms.URLField(required=False)
    body = forms.CharField(widget=forms.Textarea, max_length = 1024, required = False)
    def __init__(self, *args, **kwargs):
        choices = kwargs.pop('choices')
        super(RedditSubmitForm, self).__init__(*args, **kwargs)
        self.fields['subreddit'].choices = choices 

    def clean(self):
        cleaned_data = super(RedditSubmitForm, self).clean()
        url = cleaned_data.get("url")
        body = cleaned_data.get("body")
        if not (url or body) or (url and body):
            raise forms.ValidationError( _('One and only one of Url or Body may be specified'), code='BodyOrUrlRequired')
        return cleaned_data
