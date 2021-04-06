from __future__ import absolute_import
from django.conf.urls import include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
import django.contrib.staticfiles

# Remove RegistrationProfile widget from admin interface
from registration.admin import RegistrationProfile
admin.autodiscover()
#admin.site.unregister(RegistrationProfile)



urlpatterns = [
    # Examples:

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^scripture_game/', include('scripture_game.urls')),
    #url(r'^notes/', include('cloud_notes.urls')),
    #url(r'^memos/', include('cloud_memos.urls')),
    #url(r'^weather/', include('weather.urls')),
    #url(r'^twitter/', include('twitterapp.urls')),
    #url(r'^botnet/', include('botnet.urls')),
    #url(r'^reddit/', include('reddit.urls', namespace = 'reddit', app_name = "reddit")),
    #url(r'^room_manage/', include('room_manage.urls')),
    url(r'^bible/', include('bibleapp.urls')),
    #url(r'^prayer/', include('prayers.urls', namespace='prayers')),
    #url(r'^bots/approve/(\d+)', 'logos.views.bot_approval'),
    #url(r'^bots/deny/(\d+)', 'logos.views.bot_deny'),
    
    # parameter is room name
    #url(r'^bots/colours/$', 'logos.views.bot_colours'),
    #url(r'^bots/colours/get-room-colours/([^/]+)/([^/]+)/', 'logos.views.ajax_get_room_colours'),
    
    # Uncomment the next line to enable the admin:
    #url(r'^admin/', include(admin.site.urls)),
    
    #url(r'^static/(?P<path>.*)$', django.contrib.staticfiles.views.serve),
]
