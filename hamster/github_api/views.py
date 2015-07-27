from django.http import HttpResponse
from django.views.decorators.http import require_GET

from pipeline.executor import Executor

import logging
from pipeline.actions import TaskAction

logger = logging.getLogger(__name__)


@require_GET
def debug_view(request):
    """Debug view for local testing.
    """
    dct = {
        'task': 'print_something',
        'kwargs': {
            'the_thing': 'came from debug_view'
        },
        'handlers': [
            {
                'task': 'print_something',
                'kwargs': {
                    'the_thing': 'this is a handler!'
                },
                'predicate': "not parent",
                'handlers': [
                    {
                        'task': 'print_something',
                        'kwargs': {
                            'the_thing': 'INCEPTION!'
                        },
                    },
                ]

            },
        ]
    }
    actions = [TaskAction.from_dict(dct)]
    executor = Executor()

    count = int(request.GET.get('count', 1))
    for i in range(count):
        executor.schedule(actions, None)

    return HttpResponse()