# forms.py
from django import forms
import re

class NoteForm(forms.Form):
    title = forms.CharField(max_length=30,required=True) 
    note = forms.CharField(required=True)

class NewFolderForm(forms.Form):
    folder = forms.CharField(max_length=120,required=True)
    def clean_folder(self):
        data = self.cleaned_data['folder']
        if not re.match("[a-zA-Z_]+$", data):
            raise forms.ValidationError("folder name must be alphabetic and/or underscore")
        return data
    
class UploadFileForm(forms.Form):
    file = forms.FileField()    