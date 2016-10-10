from __future__ import absolute_import
from django import forms
from django.utils.translation import ugettext as _
from django.utils import timezone

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

class NewSubredditFeedForm(forms.Form):
    freq_choices = [(30, 'half hourly'),(60, 'hourly')]
    subreddits = forms.MultipleChoiceField(label="Subreddits to monitor")
    target = forms.ChoiceField()
    frequency = forms.ChoiceField(choices = freq_choices)
    start_date = forms.DateTimeField()
    active = forms.BooleanField(initial=True)

    def __init__(self, *args, **kwargs):
        mysubreddits = kwargs.pop('mysubreddits')
        super(NewSubredditFeedForm, self).__init__(*args, **kwargs)
        self.fields['subreddits'].choices = mysubreddits
        self.fields['target'].choices = mysubreddits

class FeedForm(forms.Form):
    freq_choices = [(30, 'half hourly'),(60, 'hourly')]
    subreddits = forms.MultipleChoiceField(label="Subreddits to monitor")
    target_sub = forms.ChoiceField(required=False, label="Target Subreddit")
    target_irc = forms.ChoiceField(required=False, label="Target IRC Room")
    frequency = forms.ChoiceField(choices = freq_choices)
    start_date = forms.DateTimeField(initial=timezone.now())
    post_limit = forms.IntegerField(initial=1, min_value = 1, max_value = 20)
    active = forms.BooleanField(required=False, initial=True)

    def __init__(self, *args, **kwargs):
        mysubreddits = kwargs.pop('mysubreddits', [])
        myircrooms = kwargs.pop('myircrooms', [])
        subreddit_choices = list(mysubreddits)
        irc_choices = list(myircrooms)
        super(FeedForm, self).__init__(*args, **kwargs)
        subreddit_choices.insert(0, (0,''))        
        irc_choices.insert(0, (0,''))
        self.fields['subreddits'].choices = mysubreddits
        self.fields['target_sub'].choices = subreddit_choices
        self.fields['target_irc'].choices = irc_choices

    def clean(self):
        cleaned_data = super(FeedForm, self).clean()
        target_sub = int(cleaned_data.get("target_sub"))
        target_irc = int(cleaned_data.get("target_irc"))
        if not (target_sub or target_irc) or (target_sub and target_irc):
            raise forms.ValidationError( _('One and only one of target subreddit or IRC may be specified'), code='SubOrIRCRequired')
        return cleaned_data

class CommentForm(forms.Form):
    body = forms.CharField(widget=forms.Textarea, max_length = 1024, required = True)
