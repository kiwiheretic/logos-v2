from __future__ import absolute_import
from django.shortcuts import render
from django.forms.models import model_to_dict

from oauth2client.client import OAuth2WebServerFlow

from .forms import SiteSetupForm
from .models import SiteModel

# Create your views here.
def site_setup(request):
    if request.method == "POST":
        form = SiteSetupForm(request.POST)
        if form.is_valid():
            SiteModel.objects.all().delete()
            client_id = form.cleaned_data['client_id']
            client_secret = form.cleaned_data['client_secret']
            mdl = SiteModel(client_id = client_id,
                    client_secret = client_secret)
            mdl.save()
    else:
        mdl = SiteModel.objects.first()
        if mdl:
            model_data = model_to_dict(mdl, fields = ['client_id', 'client_secret'])
            form = SiteSetupForm(initial=model_data)
        else:
            form = SiteSetupForm()
    return render(request, 'gcal/site_setup.html', {'form':form})

def user_setup(request):
    mdl = SiteModel.objects.first()
    flow = OAuth2WebServerFlow(client_id=mdl.client_id,
                               client_secret=mdl.client_secret,
                               scope='https://www.googleapis.com/auth/calendar',
                               redirect_uri='http://localhost:8000/callback')
    url = flow.step1_get_authorize_url() 
    return render(request, 'gcal/user_setup.html', {'url':url, 'form':None})


