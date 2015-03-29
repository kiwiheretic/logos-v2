from django.shortcuts import render
from .models import Memo

# Create your views here.
def new(request):
    context = {}
    return render(request, 'cloud_memos/new.html', context)

def inbox(request):
    memos = Memo.objects.filter(to_user = request.user)
    context = {'memos':memos}
    return render(request, 'cloud_memos/list.html', context)