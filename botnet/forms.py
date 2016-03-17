from django import forms
from .models import BotNetGroups

class SiteSetupForm(forms.Form):
    id = forms.IntegerField(required=False, widget=forms.HiddenInput)
    group = forms.CharField(max_length = 100, label="Group Name")
    rooms = forms.MultipleChoiceField()
    active = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        choices = kwargs.pop('choices', None)
        readonly = kwargs.pop('readonly_name', False)
        super(SiteSetupForm, self).__init__(*args, **kwargs)
        self.fields['rooms'].choices = choices
        self.fields['rooms'].widget.attrs['style'] = 'width:500px;height:100px'
        if readonly:
            self.fields['group'].widget.attrs['readonly'] = True

    def clean_group(self):
        group = self.cleaned_data['group']
        if not self.cleaned_data['id'] and BotNetGroups.objects.filter(group_name = group).exists():
            raise forms.ValidationError("Group already exists - choose a different group name", code="groupexists")
        # return original cleaned data
        return group


