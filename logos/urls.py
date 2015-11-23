from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

# Remove RegistrationProfile widget from admin interface
from registration.admin import RegistrationProfile
admin.autodiscover()
admin.site.unregister(RegistrationProfile)



urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'logos.views.root_url'),
    # url(r'^logos/', include('logos.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^accounts/profile/', 'logos.views.profile'),
#    url(r'^accounts/profile/', include('cloud_notes.urls')),
    
    url(r'^logos-admin/$', 'logos.views.admin'),
    url(r'^logos-admin/bots/', 'logos.views.bots'),
    
    url(r'^logos-admin/plugins/$', 'logos.views.plugins'),
    url(r'^logos-admin/plugins/network/(\d+)', 'logos.views.networkplugins'),
    url(r'^logos-admin/plugins/network/delete/(\S+)/', 'logos.views.deletenetworkplugins'),
    url(r'^logos-admin/plugins/network/room/activate/(\d+)/', 'logos.views.plugin_room_activate'),
    url(r'^logos-admin/bot-view/(\d+)', 'logos.views.bot_view'),
    
    url(r'^notes/', include('cloud_notes.urls')),
    url(r'^memos/', include('cloud_memos.urls')),
    url(r'^forum/', include('pybb.urls', namespace='pybb')),
    url(r'^bots/approve/(\d+)', 'logos.views.bot_approval'),
    url(r'^bots/deny/(\d+)', 'logos.views.bot_deny'),
    
    # parameter is room name
    url(r'^bots/colours/$', 'logos.views.bot_colours'),
    url(r'^bots/colours/get-room-colours/([^/]+)/([^/]+)/', 'logos.views.ajax_get_room_colours'),
    
    url(r'^web-views/nicks-css/', 'logos.views.nicks_css'),
    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    
    url(r'^static/(?P<path>.*)$', 'django.contrib.staticfiles.views.serve'),
)
