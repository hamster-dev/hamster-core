from django.http import HttpResponse
from django.views.decorators.http import require_GET

from pipeline.pipeline import Pipeline
from pipeline.actions import TaskAction

import logging
logger = logging.getLogger(__name__)


@require_GET
def debug_view(request):
    """Debug view for local testing.
    """

    return HttpResponse()