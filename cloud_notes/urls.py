# urls.py
from __future__ import absolute_import

from django.conf.urls import patterns, include, url
from haystack.generic_views import SearchView
from haystack.forms import SearchForm
from .views import MySearchView

# required to set an app name to resolve 'url' in templates with namespacing
app_name = "cloud_notes"

urlpatterns = patterns('cloud_notes.views',
    url(r'^$', 'list'),
    url(r'^new/', 'new_note'),
    url(r'^preview/(\d+)', 'preview'),
    url(r'^edit/(\d+)', 'edit_note'),
    url(r'^trash/(\d+)', 'trash_note'),
    url(r'^empty_trash/', 'empty_trash'),
    url(r'^delete/(\d+)', 'delete_note'),
    url(r'^upload/', 'upload_note'),
    url(r'^export/', 'export'),
    url(r'^export_all/', 'export_all'),
    url(r'^import/', 'import_file'),
    url(r'^import_all/', 'import_all'),
    url(r'^folders/', 'folders'),
    url(r'^hash_tags/', 'hash_tags'),
    url(r'^download/(\d+)', 'download'),
    url(r'^search/', MySearchView.as_view(form_class = SearchForm), name='search_view'),
)
