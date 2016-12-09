# urls.py
from __future__ import absolute_import

from django.conf.urls import include, url
from haystack.generic_views import SearchView
from haystack.forms import SearchForm
from .views import MySearchView
import cloud_notes.views

# required to set an app name to resolve 'url' in templates with namespacing
app_name = "cloud_notes"

urlpatterns = [
    url(r'^$', cloud_notes.views.list),
    url(r'^new/', cloud_notes.views.new_note),
    url(r'^preview/(\d+)', cloud_notes.views.preview),
    url(r'^edit/(\d+)', cloud_notes.views.edit_note),
    url(r'^trash/(\d+)', cloud_notes.views.trash_note),
    url(r'^empty_trash/', cloud_notes.views.empty_trash),
    url(r'^delete/(\d+)', cloud_notes.views.delete_note),
    url(r'^upload/', cloud_notes.views.upload_note),
    url(r'^export/', cloud_notes.views.export),
    url(r'^export_all/', cloud_notes.views.export_all),
    url(r'^import/', cloud_notes.views.import_file),
    url(r'^import_all/', cloud_notes.views.import_all),
    url(r'^folders/', cloud_notes.views.folders),
    url(r'^hash_tags/', cloud_notes.views.hash_tags),
    url(r'^download/(\d+)', cloud_notes.views.download),
    url(r'^search/', cloud_notes.views.MySearchView.as_view(form_class = SearchForm), name='search_view'),
]
