from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
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
    memos = Memo.objects.filter(to_user = request.user)
    context = {'memos':memos,'cat_title':'Inbox'}
    return render(request, 'cloud_memos/list.html', context)

@login_required()
def outbox(request):
    memos = Memo.objects.filter(from_user = request.user)
    context = {'memos':memos, 'cat_title':'Outbox'}
    return render(request, 'cloud_memos/list.html', context)

@login_required()
def listing(request):
    pass
    
@login_required()
def new(request):
    context = {'cat_title':'New Memo'}
    if request.method == 'POST':
        frm = MemoForm(request.POST)
        context.update({'form':frm})
        if frm.is_valid():
            to_user = User.objects.get(username=frm.cleaned_data['recipient'])
            Memo.send_memo(request.user, to_user,
                frm.cleaned_data['subject'], 
                frm.cleaned_data['message'])
            return redirect('cloud_memos.views.inbox')
        else:
            return render(request, 'cloud_memos/new.html', context)
    else:
        return render(request, 'cloud_memos/new.html', context)

        
@login_required()
def preview(request, memo_id):
    memo = get_object_or_404(Memo, pk=memo_id)
    context = {'memo':memo, 'cat_title':'Displaying Memo'}
    return render(request, 'cloud_memos/preview.html', context)

@login_required()
def trash_memo(request, memo_id):
    memo = get_object_or_404(Memo, pk=memo_id)
    context = {'memo':memo}
    if request.method == 'GET':
        return render(request, 'cloud_memos/trash_confirm.html', context)
    else:
        if 'yes' in request.POST:
            memo.delete()
        return redirect('cloud_memos.views.inbox')
        
