from __future__ import absolute_import
from django.shortcuts import render

from .models import NickHistory
# Create your views here.

def index(request):
    nh = NickHistory.objects.all().order_by('network', 'host_mask', 'nick')
    nicklist = []
    for rec in nh:
        if len(nicklist) > 0:
            if nicklist[-1].nick != rec.nick or \
               nicklist[-1].network != rec.network or \
               nicklist[-1].host_mask != rec.host_mask:
                nicklist.append(rec)
        else:
            nicklist.append(rec)
            
    return render(request, 'room_manage/index.html', {'nicklist':nicklist})
