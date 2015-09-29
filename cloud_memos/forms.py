# forms.py
from django import forms
from django.contrib.auth.models import User

class MemoForm(forms.Form):
    subject = forms.CharField(max_length=100, required=True)
    recipient = forms.CharField(max_length=40, required=True)
    message = forms.CharField(required=True)
    
    def clean_recipient(self):
        recipient = self.cleaned_data['recipient']
        try:
            u = User.objects.get(username__iexact = recipient)
        except User.DoesNotExist:
            raise forms.ValidationError('Recipient does not exist')
        return recipient