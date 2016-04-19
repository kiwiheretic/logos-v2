from __future__ import absolute_import
from django.shortcuts import render
from .forms import SiteSetupForm
from logos.roomlib import get_global_option, set_global_option
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Create your views here.
@login_required()
def site_setup(request):
    if request.method == "POST":
        form = SiteSetupForm(request.POST)
        if form.is_valid():
            api_key = form.cleaned_data['api_key']
            set_global_option('weather_api_key', api_key)
            messages.add_message(request, messages.INFO, 'API key saved successfully')
    else:
        api_key = get_global_option('weather_api_key')
        if api_key:
            form = SiteSetupForm(initial={'api_key':api_key})
        else:
            form = SiteSetupForm()
    return render(request, 'weather/site_setup.html', {'form':form})

