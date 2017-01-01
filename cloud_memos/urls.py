# urls.py
from __future__ import absolute_import
from django.conf.urls import include, url
import cloud_memos.views

urlpatterns = [
    url(r'^$', cloud_memos.views.index),
    url(r'^listing/', cloud_memos.views.listing),
    url(r'^inbox/', cloud_memos.views.inbox),
    url(r'^outbox/', cloud_memos.views.outbox),
    url(r'^new/', cloud_memos.views.new),
    url(r'^preview/(\d+)', cloud_memos.views.preview),
    url(r'^trash_memo/(\d+)', cloud_memos.views.trash_memo),
    url(r'^export/', cloud_memos.views.export),

    url(r'^su-export/', cloud_memos.views.superuser_export),
    url(r'^su-import/', cloud_memos.views.superuser_import),

    #    url(r'^folders/', 'folders'),
]
