from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = patterns('',
    url(r'^hookshot/', include('hookshot.urls')),
    url(r'^admin/', include(admin.site.urls)),
    )

# statcfiles under gunicorn
import os
server = os.environ.get('SERVER_SOFTWARE')
if server and server.startswith('gunicorn'):
    urlpatterns += staticfiles_urlpatterns()

