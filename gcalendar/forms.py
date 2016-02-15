from django import forms

class SiteSetupForm(forms.Form):
    client_id = forms.CharField(max_length=200)
    client_secret = forms.CharField(max_length=200)


class EventForm(forms.Form):
    date_input_formats = ['%d/%m/%y', '%d/%m/%Y']
    recur_choices = (('NR', 'No recurring'), ('RW', 'Recur Weekly'))

    summary = forms.CharField(max_length=100, required = True)
    location = forms.CharField(max_length=100, required = False)
    start_date = forms.DateField(input_formats = date_input_formats, required=True)
    start_time = forms.TimeField(required = False)
    duration = forms.IntegerField(label='Duration (minutes)', initial='60', min_value = 0)
    recurring = forms.ChoiceField(choices = recur_choices)
    description = forms.CharField(max_length=1024,
            required = False,
            widget=forms.Textarea)
