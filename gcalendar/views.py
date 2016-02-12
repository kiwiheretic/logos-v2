from __future__ import absolute_import
from django.shortcuts import render, redirect
from django.forms.models import model_to_dict
from django.contrib import messages

from oauth2client.client import OAuth2WebServerFlow
from oauth2client.django_orm import Storage

from .forms import SiteSetupForm
from .models import SiteModel, FlowModel, CredentialsModel

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
    storage = Storage(CredentialsModel, 'id', request.user, 'credential')
    credentials = storage.get()
    mdl = SiteModel.objects.first()
    flow = OAuth2WebServerFlow(client_id=mdl.client_id,
                               client_secret=mdl.client_secret,
                               scope='https://www.googleapis.com/auth/calendar.readonly',
                               redirect_uri='http://localhost:8000/gcal/callback')
    f, created = FlowModel.objects.get_or_create(id = request.user)
    f.flow = flow
    f.save()
    url = flow.step1_get_authorize_url() 
    if credentials:
        return render(request, 'gcal/user_setup.html', {'credentials':credentials, 'url':url})
    else:

        return render(request, 'gcal/user_setup.html', {'url':url})


def oauth_callback(request):
    code = request.GET['code']
    flow = FlowModel.objects.get(id = request.user).flow
    credentials = flow.step2_exchange(code)
    storage = Storage(CredentialsModel, 'id', request.user, 'credential')
    storage.put(credentials)
    messages.add_message(request, messages.INFO, 'Google Authentication Successful')
    return redirect('user_setup')

