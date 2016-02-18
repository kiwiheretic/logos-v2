from __future__ import absolute_import
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import UserSettingsForm
from logos.roomlib import set_user_option

# Create your views here.
@login_required()
def user_settings(request):
    if request.method == "GET":
        form = UserSettingsForm()
    else: #POST
        form = UserSettingsForm(request.POST)
        if form.is_valid():
            translation = form.cleaned_data['preferred_translation']
            if translation:
                set_user_option(request.user, "translation", translation)
                messages.add_message(request, messages.INFO, 'Bible Plugin Settings Updated Successfully')
                return redirect('plugins')


    return render (request, 'bible/user_settings.html', {'form':form})

