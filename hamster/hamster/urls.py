from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from rest_framework import routers
from jobs import views

router = routers.DefaultRouter()
router.register(r'jobs', views.JobViewSet)


urlpatterns = patterns('',
    # Examples:
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    #url(r'^$', 'hamster.views.home', name='home'),
    #url(r'^api/$', include('jobs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
