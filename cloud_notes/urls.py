# urls.py
from django.conf.urls import patterns, include, url

urlpatterns = patterns('cloud_notes.views',
    url(r'^$', 'list'),
    url(r'^new/', 'new_note'),
    url(r'^preview/(\d+)', 'preview'),
    url(r'^edit/(\d+)', 'edit_note'),
    url(r'^trash/(\d+)', 'trash_note'),
    url(r'^delete/(\d+)', 'delete_note'),
    url(r'^export/', 'export'),
    url(r'^folders/', 'folders'),
)