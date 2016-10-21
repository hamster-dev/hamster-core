
from django.conf.urls import url, patterns
from .api import github_webhook

urlpatterns = patterns('',
    url(r'^hook/$', github_webhook, name='github-webhook'),
)


