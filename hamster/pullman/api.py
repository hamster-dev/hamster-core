
from django.http import HttpResponse
from django.conf import settings
from rest_framework.decorators import api_view

from pipeline_django.models import PipelineEventHandler

from pullman.events import GithubWebhookEvent

import logging
logger = logging.getLogger(__name__)



def handle_github_events(request):
    """Route github events to the appropriate event handler.
    """
    events = GithubWebhookEvent.find_matching(request)
    if not len(events):
        return []

    logger.debug("found events {}".format(events))
    return PipelineEventHandler.objects.handle_events(events)


hook_methods = ('POST',) if not settings.DEBUG else ('POST', 'GET')

@api_view(hook_methods)
def github_webhook(request):
    """View for handling github webhooks.
    """
    try:
        # ignore the return value, we don't care.
        handle_github_events(request)

    except:
        import sys, traceback
        ex_type, ex, tb = sys.exc_info()
        logger.error("{}\n{}".format(str(ex), traceback.format_tb(tb)))

    finally:
        # always return 200 to github, it doesnt care about our problems...
        #TODO this should be DRF-specific??
        return HttpResponse()


