from django import forms

class SiteSetupForm(forms.Form):
    api_key = forms.CharField(max_length=200)
