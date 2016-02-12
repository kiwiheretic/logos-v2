from django import forms

class SiteSetupForm(forms.Form):
    client_id = forms.CharField(max_length=200)
    client_secret = forms.CharField(max_length=200)
