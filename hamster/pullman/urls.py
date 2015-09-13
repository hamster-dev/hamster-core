
from django.conf.urls import url, patterns
from .api import github_webhook
from .views import debug_view

urlpatterns = patterns('',
    url(r'^hook/$', github_webhook, name='github-webhook'),
    url(r'^debug/$', debug_view, name='debug'),
)


