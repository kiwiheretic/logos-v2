from __future__ import absolute_import
from django.conf.urls import include, url
import logos.views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
import django.contrib.staticfiles

# Remove RegistrationProfile widget from admin interface
from registration.admin import RegistrationProfile
admin.autodiscover()
#admin.site.unregister(RegistrationProfile)



urlpatterns = [
    # Examples:
    url(r'^$', logos.views.root_url),
    url(r'^bot-commands/$', logos.views.bot_commands),
    url(r'^logos/user-settings/$', logos.views.user_settings),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^accounts/profile/', logos.views.profile),
    url(r'^logos/preferences/', logos.views.preferences),
    
    url(r'^logos-admin/$', logos.views.admin),
#    url(r'^logos-admin/bots/', logos.views.bots),
    
    url(r'^logos-admin/plugins/$', logos.views.plugins, name='plugins'),
    url(r'^logos-admin/plugins/network/(\d+)', logos.views.networkplugins),
    url(r'^logos-admin/plugins/network/delete/(\S+)/', logos.views.deletenetworkplugins),
    url(r'^logos-admin/plugins/network/room/activate/(\d+)/', logos.views.plugin_room_activate),
    url(r'^logos-admin/bot-view/(\d+)', logos.views.bot_view),
    
    url(r'^scripture_game/', include('scripture_game.urls')),
    url(r'^notes/', include('cloud_notes.urls')),
    url(r'^memos/', include('cloud_memos.urls')),
    #url(r'^weather/', include('weather.urls')),
    #url(r'^twitter/', include('twitterapp.urls')),
    url(r'^botnet/', include('botnet.urls')),
    #url(r'^reddit/', include('reddit.urls', namespace = 'reddit', app_name = "reddit")),
    #url(r'^room_manage/', include('room_manage.urls')),
    url(r'^bible/', include('bibleapp.urls')),
    #url(r'^prayer/', include('prayers.urls', namespace='prayers')),
    #url(r'^bots/approve/(\d+)', 'logos.views.bot_approval'),
    #url(r'^bots/deny/(\d+)', 'logos.views.bot_deny'),
    
    # parameter is room name
    #url(r'^bots/colours/$', 'logos.views.bot_colours'),
    #url(r'^bots/colours/get-room-colours/([^/]+)/([^/]+)/', 'logos.views.ajax_get_room_colours'),
    
    url(r'^web-views/nicks-css/', logos.views.nicks_css),
    # Uncomment the next line to enable the admin:
    #url(r'^admin/', include(admin.site.urls)),
    
    #url(r'^static/(?P<path>.*)$', django.contrib.staticfiles.views.serve),
]
