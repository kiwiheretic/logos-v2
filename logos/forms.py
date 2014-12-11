# forms.py
from django import forms

class SettingsForm(forms.Form):
    rpc_host = forms.CharField(label='RPC Host',max_length=20, 
                               widget=forms.TextInput(attrs={'size':20}))
    rpc_port = forms.CharField(label='RPC Port',max_length=7, 
                               widget=forms.TextInput(attrs={'size':8}))
    
NETWORK_CHOICES = (
    ('UN', 'Undernet'),
    ('C4', 'Chat4all'),
    ('CH', 'Chatopia'),
    ('RZ', 'Rizon'),
    ('MY', 'MyIRC'),
)
class RequestBotForm(forms.Form):
    network = forms.ChoiceField( choices=NETWORK_CHOICES )
    room = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'placeholder':'#mychat'}))
    password = forms.CharField(max_length=20, label="Bot Password", widget=forms.PasswordInput())
    confirm = forms.CharField(max_length=20, label="Confirm Password", widget=forms.PasswordInput())
    
    def clean_password(self):
        data = self.cleaned_data['password']
        if ' ' in data:
            raise forms.ValidationError("Password must not contain spaces")
        return data
    
    def clean(self):
        cleaned_data = super(RequestBotForm, self).clean()
        pw = self.cleaned_data.get('password')
        data = self.cleaned_data.get('confirm')
        if pw != data:
            raise forms.ValidationError("Password and confirmation must match")
        return data