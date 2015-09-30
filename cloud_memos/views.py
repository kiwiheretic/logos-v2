from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib import messages

import json
from datetime import datetime
import pytz
from .models import Memo, Folder
from .forms import MemoForm

# Current limitations and ToDos:
# - deleting a memo deletes from recipients inbox AND senders outbox
#   (ie: no reference counting)
# - Add in paginator for memo list 


@login_required()
def index(request):
    return redirect('cloud_memos.views.inbox')
    
@login_required()
def inbox(request):
    request.session['box'] = 'inbox'
    memos = Memo.objects.filter(folder__name = 'inbox', to_user = request.user).order_by('-id')
    context = {'memos':memos,'cat_title':'Inbox'}
    return render(request, 'cloud_memos/list.html', context)

@login_required()
def outbox(request):
    request.session['box'] = 'outbox'
    memos = Memo.objects.filter(folder__name = 'outbox', from_user = request.user).order_by('-id')
    context = {'memos':memos, 'cat_title':'Outbox'}
    return render(request, 'cloud_memos/list.html', context)

@login_required()
def listing(request):
    return redirect('cloud_memos.views.inbox')
    
@login_required()
def new(request):
    userlist = []
    for user in User.objects.all():
        userlist.append(user.username)
    context = {'cat_title':'New Memo', 'userlist':userlist}
    if request.method == 'POST':
        frm = MemoForm(request.POST)
        context.update({'form':frm})
        if frm.is_valid():
            to_user = User.objects.get(username__iexact=frm.cleaned_data['recipient'])
            Memo.send_memo(request.user, to_user,
                frm.cleaned_data['subject'], 
                frm.cleaned_data['message'])
            messages.success(request, 'Your memo was successfully delivered.')
            return redirect('cloud_memos.views.inbox')
        else:
            return render(request, 'cloud_memos/new.html', context)
    else:
        return render(request, 'cloud_memos/new.html', context)

        
@login_required()
def preview(request, memo_id):
    memo = get_object_or_404(Memo, pk=memo_id)
    context = {'memo':memo, 'cat_title':'Displaying Memo'}
    # mark this memo as read
    memo.viewed_on = datetime.now(pytz.utc)
    memo.save()
    
    return render(request, 'cloud_memos/preview.html', context)

@login_required()
def trash_memo(request, memo_id):
    memo = get_object_or_404(Memo, pk=memo_id)
    context = {'memo':memo}
    if request.method == 'GET':
        return render(request, 'cloud_memos/trash_confirm.html', context)
    else:
        if 'yes' in request.POST:
            subject = memo.subject
            memo.delete()
            messages.success(request, 'Your memo "%s" was permanently deleted.' % (subject,))
        if request.session.has_key('box'):
            if request.session['box'] == 'inbox':
                return redirect('cloud_memos.views.inbox')
            elif request.session['box'] == 'outbox':
                return redirect('cloud_memos.views.outbox')
        else:
            return redirect('cloud_memos.views.inbox')
        

@login_required()
def export(request):
    memos = Memo.objects.filter(to_user = request.user)
    memo_list = aggregate_memos(memos)
    data_version = 0.90

    dt_now = str(datetime.now(pytz.utc))
    data = {'data_version':data_version, 
        'date_exported':dt_now,
        'memos':memo_list } 
    data = {'data_version':data_version, 'memos':memo_list } # data version 0.1
    all_data = json.dumps(data, indent=4)
    response = HttpResponse(all_data, content_type='application/json')
    response['Content-Disposition'] = \
        "attachment; filename=\"user_memos_{}.json\"".format(data_version)
    return response

        
@login_required()
def superuser_import(request):
    pass

            
@login_required()
def superuser_export(request):
   if request.user.is_superuser:

        memos = Memo.objects.all()
        memo_list = aggregate_memos(memos)
        data_version = 0.90
        dt_now = str(datetime.now(pytz.utc))
        data = {'data_version':data_version, 
            'date_exported':dt_now,
            'memos':memo_list } 
        all_data = json.dumps(data, indent=4)
        response = HttpResponse(all_data, content_type='application/json')
        response['Content-Disposition'] = \
            "attachment; filename=\"sys_memos_{}.json\"".format(data_version)
        return response

def aggregate_memos(memos):
    memo_list = []
    for memo in memos:
        memo_dict = {}
        
        memo_dict['ID'] = memo.id
        memo_dict['created'] = str(memo.created )
        memo_dict['viewed_on'] = str(memo.viewed_on)
        memo_dict['subject'] = memo.subject
        memo_dict['text'] = memo.text
        memo_dict['from_user'] = memo.from_user.username
        memo_dict['to_user'] = memo.to_user.username
        memo_dict['folder'] = [memo.folder.id, memo.folder.name]
        # this one could explode on null reference
        try:
            memo_dict['forwarded_by']  = memo.forwarded_by.username
        except AttributeError:
            memo_dict['forwarded_by']  = None
        
        memo_list.append(memo_dict)
    return memo_list