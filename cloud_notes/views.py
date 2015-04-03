from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core import serializers
from itertools import chain
from django.http import HttpResponse, HttpResponseRedirect
import os
import json

from forms import NoteForm
from models import Note, Folder
from django.contrib.auth.models import User
# Create your views here.
from datetime import datetime
from forms import NewFolderForm, UploadFileForm

@login_required()
def folders(request):
    folders = Folder.objects.all()
    context = {'folders':folders}
    if request.method == 'POST':
        # changing to a different folder
        if "change_folder" in request.POST:
            request.session['notes_folder'] = request.POST['folder']
            # If we are changing folders we don't 
            # want to keep to what page we were on in
            # the other folder.
            if 'page' in request.session:
                del request.session['page']
            return redirect('cloud_notes.views.list')
        if "create_folder" in request.POST:
            form = NewFolderForm(request.POST)
            if form.is_valid():
                folder_name = form.cleaned_data['folder']
                folder = Folder(name = folder_name)
                folder.save()
                return redirect('cloud_notes.views.list')
            else:
                context['form'] = form
                return render(request, 'cloud_notes/folders.html', context)
    else:
        return render(request, 'cloud_notes/folders.html', context)
    
@login_required()
def list(request):
    if 'notes_folder' in request.session:
        folder = Folder.objects.get(pk = request.session['notes_folder'])
    else:
        folder = Folder.objects.get(name = "Main")
    notes_list = Note.objects.filter(folder = folder, user=request.user).\
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
    context = {'notes':notes, 'folder':folder}
    return render(request, 'cloud_notes/list.html', context)
    
@login_required()
def preview(request, note_id):
    note = Note.objects.get(pk=note_id)
    if request.method == "POST":
        if "move_folder" in request.POST:
            folder = Folder.objects.get(pk=request.POST['folder'])
            note.folder = folder
            note.save()
            return redirect('cloud_notes.views.list')
            

    else:
        folders = Folder.objects.all()
        context = {'note':note, 'folders':folders}
        return render(request, 'cloud_notes/preview.html', context)
    
@login_required()
def new_note(request):
    if request.method == 'GET':
        context = {'suppress_menu':True}
        return render(request, 'cloud_notes/new.html', context)
    elif request.method == 'POST':
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
def edit_note(request, note_id):
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
        form = NoteForm(note)
        context = {'form':form, 'suppress_menu':True}
        return render(request, 'cloud_notes/new.html', context)
        
@login_required()
def trash_note(request, note_id):
    trash = Folder.objects.get(name="Trash")
    note = Note.objects.get(pk=note_id)
    note.folder = trash
    note.save()
    return redirect('cloud_notes.views.list')

@login_required()
def delete_note(request, note_id):
    note = Note.objects.get(pk=note_id)
    note.delete()
    return redirect('cloud_notes.views.list')
        
@login_required()
def export(request):
    context = {}
    folders = serializers.serialize('json', Folder.objects.all())
    notes = serializers.serialize('json',Note.objects.filter(user=request.user))
    data = [ folders, notes ]
    all_data = json.dumps(data)
    response = HttpResponse(all_data, content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename="notes.json"'
    return response

@login_required()
def export_all(request):
    if request.user.is_superuser:
        context = {}
        users = json.loads(serializers.serialize('json', User.objects.all()))
        folders = json.loads(serializers.serialize('json', Folder.objects.all()))
        notes = json.loads(serializers.serialize('json',Note.objects.all()))
        data_version = 0.11
        data = [ data_version, users, folders, notes ] # data version 0.1
        all_data = json.dumps(data)
        response = HttpResponse(all_data, content_type='application/json')
        response['Content-Disposition'] = \
            "attachment; filename=\"notes_{}.json\"".format(data_version)
        return response

@login_required()
def import_all(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        context = {'form':form}
        if form.is_valid():
            handle_uploaded_file(request.FILES['file'], request.user)
            return redirect('cloud_notes.views.list')            
    else:
        form = UploadFileForm()
        context = {'form':form}
    return render(request, 'cloud_notes/import_file.html', context)
    
@login_required()
def import_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        context = {'form':form}
        if form.is_valid():
            handle_uploaded_file(request.FILES['file'], request.user)
            return redirect('cloud_notes.views.list')            
    else:
        form = UploadFileForm()
        context = {'form':form}
    return render(request, 'cloud_notes/import_file.html', context)

def handle_uploaded_file(f, user):
    with open('notes.json', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
        f.close()
    with open('notes.json', 'r') as fh:
        json_data = json.load(fh)
        fh.close()
    import pdb; pdb.set_trace()
    version, folder_data, notes_data = json_data
    for folder in folders:
        fname = folder['fields']['name']
        if not Folder.objects.filter(name = fname).exists():
            fldr = Folder(name = fname)
            fldr.save()
    for note in notes:
        title = note['fields']['title'] 
        created = note['fields']['created_at'] 
        modified = note['fields']['modified_at'] 
#        post_type = note['fields']['post_type'] 
        note_txt = note['fields']['note']
        foldr_id = note['fields']['folder']
        folder = Folder.objects.get(pk=foldr_id)
        if not Note.objects.filter(title = title, created_at = created).exists():
            new_note = Note(title = title, created_at = created, user = user,
                        modified_at = modified, note = note_txt, folder = folder)
            new_note.save()
        

#@login_required()
#def file_uploaded(request):
#    context = {}
#    return render(request, 'cloud_notes/file_uploaded.html', context)