from __future__ import absolute_import

from django import forms
from .models import BibleTranslations

class UserSettingsForm(forms.Form):
    preferred_translation = forms.ChoiceField()
    def __init__(self, *args, **kwargs):
        super(UserSettingsForm, self).__init__(*args, **kwargs)
        choices = [('', 'Use room translation')]
        for trans in BibleTranslations.objects.all():
            choices.append((trans.name, trans.name))
        self.fields['preferred_translation'].choices = choices 
