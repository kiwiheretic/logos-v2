# Create your views here.
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
            consumer_key = form.cleaned_data['consumer_key']
            consumer_secret = form.cleaned_data['consumer_secret']
            access_token = form.cleaned_data['access_token']
            token_secret = form.cleaned_data['token_secret']
            set_global_option('twitter-consumer-key', consumer_key)
            set_global_option('twitter-consumer-secret', consumer_secret)
            set_global_option('twitter-access-token', access_token)
            set_global_option('twitter-token-secret', token_secret)
            messages.add_message(request, messages.INFO, 'API key saved successfully')
    else:
        consumer_key = get_global_option('twitter-consumer-key')
        consumer_secret = get_global_option('twitter-consumer-secret')
        access_token = get_global_option('twitter-access-token')
        token_secret = get_global_option('twitter-token-secret')
        init = {'consumer_key':consumer_key, 'consumer_secret':consumer_secret,
                'access_token':access_token, 'token_secret':token_secret}
        form = SiteSetupForm(initial=init)
    return render(request, 'twitter/site_setup.html', {'form':form})

