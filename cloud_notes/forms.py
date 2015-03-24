# forms.py
from django import forms

class NoteForm(forms.Form):
    title = forms.CharField(max_length=30,required=True) 
    note = forms.CharField(required=True)

