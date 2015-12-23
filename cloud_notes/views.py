from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core import serializers
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import timezone
from django.contrib import auth  # .models.DoesNotExist
import os
import json
import re

from itertools import chain

from forms import NoteForm
from models import Note, Folder, HashTags
from django.contrib.auth.models import User
# Create your views here.
from datetime import datetime
from forms import NewFolderForm, UploadFileForm

import logging

from django.conf import settings
logger = logging.getLogger(__name__)
logging.config.dictConfig(settings.LOGGING)


@login_required()
def hash_tags(request):
    
    # putting an .exclude(notes__folder__name = 'Trash') will exclude
    # a tag that has *any* tagged note in Trash.  We want to
    # check for *all* !!  Hence the for loop.
    
    my_hash_tags = HashTags.objects.filter(user=request.user).order_by('hash_tag', 'notes__folder__name').distinct()
    tag_list = []
    for tag in my_hash_tags:
        if tag.notes.exclude(folder__name = 'Trash').count() > 0:
            if tag not in tag_list: tag_list.append(tag)
    context = {'tags':tag_list}
    return render(request, 'cloud_notes/hash_tags.html', context)

@login_required()
def folders(request):
    folders = Folder.objects.filter(user=request.user)
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
        folder, _ = Folder.objects.get_or_create(name = "Main", user=request.user)
        trash_folder, _ = Folder.objects.get_or_create(name = "Trash", user=request.user)
        
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
        folders = Folder.objects.filter(user = request.user)
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
                if 'notes_folder' in request.session:
                    fldr = Folder.objects.get(pk=request.session['notes_folder'], user=request.user)
                else:
                    fldr = Folder.objects.get(name="Main", user=request.user)
                
                # Don't allow user to inadvertently create note in Trash
                if fldr.name == 'Trash':
                    fldr = Folder.objects.get(name="Main", user=request.user)
                
                
                obj = Note()
                obj.title = form.cleaned_data['title']
                obj.note = form.cleaned_data['note']
                obj.post_type = 'note'
                obj.created_at = datetime.utcnow()
                obj.modified_at = datetime.utcnow()
                obj.user = request.user
                obj.folder = fldr
                obj.save()
                
                return redirect('cloud_notes.views.list')
            else:
                print form.errors
                return render(request, 'cloud_notes/new.html', context)

@login_required()
def edit_note(request, note_id):
    if request.method == 'POST':
        if "save" in request.POST:
            note = Note.objects.get(pk=note_id)
            note.title = request.POST['title']
            note.note = request.POST['note']
            note.modified_at = timezone.now()
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
    trash = Folder.objects.get(name="Trash", user=request.user)
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
def empty_trash(request):
    if request.method == "POST":
        if request.POST.has_key('EmptyTrash'):
            trash = Folder.objects.get(user=request.user, name="Trash")
            trash.note_set.all().delete()
            return redirect("cloud_notes.views.list")
    else: # GET
        return render(request, "cloud_notes/empty_trash.html")

def serialize_notes(notes):
    note_list = []
    for note in notes:
        note_dict = {}
        
        note_dict['created_at'] = str(note.created_at )
        note_dict['modified_at'] = str(note.modified_at)
        note_dict['post_type'] = note.note_type 
        note_dict['title'] = note.title
        note_dict['note'] = note.note
        note_dict['folder'] = note.folder.name
        try:
            note_dict['user']  = note.user.username
        except Exception as e:
            # Convoluted catch of models.DoesNotExist exception because its an
            # instance exception only but is not present in its
            # proper normal class when note.user == None (which is a data violation anyway)
            if 'DoesNotExist' == e.__class__.__name__:
                note_dict['user']  = None
            else:
                raise e
        note_list.append(note_dict)
  
    data_version = 0.11

    data = [ data_version, note_list ] # data version 0.1
    note_data = json.dumps(data)
    return note_data
    

    
@login_required()
def export(request):
    context = {}
    notes = Note.objects.filter(user=request.user)
    all_data = serialize_notes(notes)
    response = HttpResponse(all_data, content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename="notes.json"'
    return response

@login_required()
def export_all(request):
    if request.user.is_superuser:
        note_list = []
        notes = Note.objects.all()
        all_data = serialize_notes(notes)
        response = HttpResponse(all_data, content_type='application/json')
        response['Content-Disposition'] = \
            "attachment; filename=\"all_notes.json\""
        return response

@login_required()
def import_all(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        context = {'form':form}
        if form.is_valid():
            handle_uploaded_json_file(request.FILES['file'], request.user)
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
            handle_uploaded_json_file(request.FILES['file'], request.user)
            return redirect('cloud_notes.views.list')            
    else:
        form = UploadFileForm()
        context = {'form':form}
    return render(request, 'cloud_notes/import_file.html', context)

@transaction.atomic
def handle_uploaded_json_file(f, user):
    
    def convert_date(str_date):
        new_str = str_date.replace('+00:00','')
        try:
            new_dt = datetime.strptime(new_str, '%Y-%m-%d %H:%M:%S.%f')
        except ValueError:
            new_dt = datetime.strptime(new_str, '%Y-%m-%d %H:%M:%S')
        return new_dt
    
    with open('notes.json', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
        f.close()
    with open('notes.json', 'r') as fh:
        json_data = json.load(fh)
        fh.close()
    
    version, notes = json_data
    
    # for user in User.objects.all():
        # if not Folder.)objects.filter(user = user, name = "Main").exists():
            # folder = Folder(name="Main", user = user)
            # folder.save()
        # if not Folder.objects.filter(user = user, name = ")Trash").exists():
            # folder = Folder(name="Trash", user = u)ser)
            # folder.save()  
          
    for note in notes:
        created_at = convert_date(note['created_at'])
        title = note['title']
        username = note['user']

        # TODO: If user is blank we need to assign to a default user.  For now just skip.
        # Its technically a database integrity violation anyway.
        if username is None: continue

        user = User.objects.get(username = username)        

        if not Note.objects.filter(title = title, 
                               created_at = created_at).exists():
            new_note = Note()
            new_note.title =  title
            new_note.created_at = created_at
            new_note.modified_at = convert_date(note['modified_at'])
            new_note.note_type = note['post_type'] 
            new_note.note = note['note']
            foldr = note['folder']
            
            
            try:
                folder = Folder.objects.get(name = foldr, user = user)
            except Folder.DoesNotExist:
                folder = Folder(name = foldr, user = user)
                folder.save()
            new_note.folder = folder
            new_note.user = user
            new_note.save()
        
@login_required()
def download(request, id):
    context = {}
    # TODO: I am failing to check I own the note here!!
    note = get_object_or_404(Note, pk=id)
    content = note.note
    data = "##> ID : %d\n" % (note.id,)
    data += "##> Title : %s\n" % (note.title,)
    data += "##> Do NOT remove these lines if you plan to re-upload.  \n"
    data += "##> They will be removed automatically upon re-upload\n"
    data += content

    response = HttpResponse(data, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="notes_%d.txt"' % (note.id,)
    return response

def handle_uploaded_file(f, user):    
    if f.content_type != 'text/plain':
        raise Exception('Invalid File Type')
    filename = 'notes_%s.txt' % (user.username,)
    with open(filename, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
        f.close()
    with open(filename, 'r') as fh:
        id = None
        s = ""
        for line in fh.readlines():
            print (line)
            if line.startswith('##>'):
                mch = re.search(r"ID :\s+(\d+)", line)
                if mch:
                    id = int(mch.group(1))
            else:
                s += line
        if not id:
            raise Exception('Improperly formatted uploaded file')
        return (id, s)
    
        
        
@login_required()
def upload_note(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        context = {'form':form}
        if form.is_valid():
            id, note_contents = handle_uploaded_file(request.FILES['file'], request.user)
            note = get_object_or_404(Note, pk=id)
            note.note = note_contents
            note.save()
            return redirect('cloud_notes.views.preview', id)            
    else:
        form = UploadFileForm()
        context = {'form':form}
    return render(request, 'cloud_notes/import_file.html', context)

