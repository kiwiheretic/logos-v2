from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from forms import NoteForm
from models import Note, Folder
# Create your views here.
from datetime import datetime

@login_required()
def folders(request):
    folders = Folder.objects.all()
    context = {'folders':folders}
    return render(request, 'cloud_notes/folders.html', context)
    
@login_required()
def list(request):
    notes_list = Note.objects.filter(folder__name = "Main", user=request.user).\
        order_by('-modified_at')
    paginator = Paginator(notes_list, 10) # Show 10 contacts per page

    page = request.GET.get('page')
    
    # work with the page in session as we use the session
    # to keep track of what page we were last on.
    if page is None and 'page' in request.session:
        page = request.session['page']

    try:
        notes = paginator.page(page)
        request.session['page'] = page
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        notes = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        notes = paginator.page(paginator.num_pages)
    context = {'notes':notes}
    return render(request, 'cloud_notes/list.html', context)
    
@login_required()
def preview(request, note_id):
    note = Note.objects.get(pk=note_id)
    context = {'note':note}
    return render(request, 'cloud_notes/preview.html', context)
    
@login_required()
def new_memo(request):
    if request.method == 'GET':
        context = {'suppress_menu':True}
        return render(request, 'cloud_notes/new.html', context)
    elif request.method == 'POST':
        print request.POST
        if "cancel" in request.POST:
            return redirect('cloud_notes.views.list')
        else:
            form = NoteForm(request.POST)
            context = {'form':form}
            
            if form.is_valid():
                # do stuff
                # ...
                main = Folder.objects.get(name="Main")
                obj = Note()
                obj.title = form.cleaned_data['title']
                obj.note = form.cleaned_data['note']
                obj.post_type = 'note'
                obj.created_at = datetime.utcnow()
                obj.modified_at = datetime.utcnow()
                obj.user = request.user
                obj.folder = main
                obj.save()
                
                return redirect('cloud_notes.views.list')
            else:
                print form.errors
                return render(request, 'cloud_notes/new.html', context)

@login_required()
def edit_memo(request, note_id):
    if request.method == 'POST':
        if "save" in request.POST:
            print request.POST
            note = Note.objects.get(pk=note_id)
            note.title = request.POST['title']
            note.note = request.POST['note']
            note.modified_at = datetime.utcnow()
            note.save()
        else:
            print "note not saved"
        return redirect('cloud_notes.views.preview', note_id)
    else: # GET
        note = Note.objects.get(pk=note_id)
        context = {'note':note, 'suppress_menu':True}
        return render(request, 'cloud_notes/new.html', context)
        
@login_required()
def trash_memo(request, note_id):
    trash = Folder.objects.get(name="Trash")
    note = Note.objects.get(pk=note_id)
    note.folder = trash
    note.save()
    return redirect('cloud_notes.views.list')
    
@login_required()
def export(request):
    context = {}
    return render(request, 'cloud_notes/export.html', context)