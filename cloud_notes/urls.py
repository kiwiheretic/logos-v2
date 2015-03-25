# urls.py
from django.conf.urls import patterns, include, url

urlpatterns = patterns('cloud_notes.views',
    url(r'^$', 'list'),
    url(r'^new/', 'new_memo'),
    url(r'^preview/(\d+)', 'preview'),
    url(r'^edit/(\d+)', 'edit_memo'),
    url(r'^trash/(\d+)', 'trash_memo'),
    url(r'^export/', 'export'),
    url(r'^folders/', 'folders'),
)