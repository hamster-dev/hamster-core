
from django.http import HttpResponse
from django.conf import settings
from rest_framework.decorators import api_view

from pipeline_django.models import PipelineEventHandler

from github_api.events import GithubEvent

import logging
logger = logging.getLogger(__name__)



def handle_github_events(event_type, request_data):
    """Route github events to the appropriate event handler."""

    return PipelineEventHandler.handle_events(
        GithubEvent, request_data, event_type
    )

hook_methods = ('POST',) if not settings.DEBUG else ('POST', 'GET')

@api_view(hook_methods)
def github_webhook(request):
    """View for handling github webhooks.
    """
    try:
        event_type = request.META.get('HTTP_X_GITHUB_EVENT')
        request_data = request.data

        # ignore the return value, we don't care.
        handle_github_events(event_type, request_data)

    except Exception as ex:
        import sys, traceback
        ex_type, ex, tb = sys.exc_info()
        logger.error("{}\n{}".format(str(ex), traceback.format_tb(tb)))

    finally:
        # always return 200 to github, it doesnt care about our problems...
        #TODO this should be DRF-specific??
        return HttpResponse()


