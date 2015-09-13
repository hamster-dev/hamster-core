try:
    import mock
except ImportError:
    from unittest import mock
import pytest

from rest_framework.test import APIRequestFactory

from pullman.sources import PullRequest
from pullman.api import github_webhook, handle_github_events

from pipeline_django.models import PipelineEventHandler


@pytest.fixture
def event_handlers(db):

    PipelineEventHandler.objects.create(
        name="pull_request_open_hamster-six",
        events=[
            'pull_request.opened'
        ],
        criteria=[
            ['source.repository', 'is', 'hamster-ci'],
            ['source.number', 'is', 5]
        ],
        actions=[
            {
                'name': 'get_one',
                'action': 'return_one'
            }
        ]
    )
    PipelineEventHandler.objects.create(
        name="pull_request_open_two",
        events=[
            'pull_request.opened'
        ],
        criteria=None,
        actions=[]
    )
    PipelineEventHandler.objects.create(
        name="pull_request_open_three",
        events=[
            'pull_request.opened'
        ],
        criteria=[

        ],
        actions=[]
    )
    PipelineEventHandler.objects.create(
        name="pull_request_open_four",
        events=[
            'pull_request.opened'
        ],
        criteria=[

        ],
        actions=[]
    )


def test_event_handler_actions_scheduled(db, monkeypatch, pullrequest_hook_open_data):
    """Test that Executor.schedule() is called for a given event/handler"""
    # stick something in the database; 'db' fixture will ensure it's
    # deleted after the test
    PipelineEventHandler.objects.create(
        name="pull_request_open",
        events=[
            'pull_request.opened'
        ],
        criteria=[
            ['source.repository', 'is', pullrequest_hook_open_data['repository']['name']],
            ['source.number', 'is', pullrequest_hook_open_data['number']]
        ],
        actions=[
            {
                'name': 'get_one',
                'action': 'dummy_action'
            }
        ]
    )

    # craft a request object for the webhook view
    request = APIRequestFactory().post(
        'pipeline/hook/', pullrequest_hook_open_data,
        format='json',
        HTTP_X_GITHUB_EVENT='pull_request'
    )

    # patch Executor.schedule since we don't actually want to call the tasks
    null_executor = mock.Mock()
    import pipeline.pipeline
    monkeypatch.setattr(
        pipeline.pipeline.Pipeline,
        'schedule', null_executor
    )

    # # get a referennce to the actions that we expect to be called
    # actions = PipelineEventHandler.objects.get(
    #     name="pull_request_open_hamster-five"
    # ).action_objects

    response = github_webhook(request)

    assert null_executor.called
    assert response.status_code == 200

    source = null_executor.call_args[0][0]
    assert isinstance(source, PullRequest)
    assert source.repository == \
           pullrequest_hook_open_data['repository']['name']
    assert source.number == pullrequest_hook_open_data['number']

    build_kwargs = null_executor.call_args[1]
    assert build_kwargs == {'event': 'pull_request.opened'}


def test_event_handler_tasks_executed(db, pullrequest_hook_open_data):
    """Test that the actions associated with an event handler are executed."""
    PipelineEventHandler.objects.create(
        name="pull_request_open_hamster-five",
        events=[
            'pull_request.opened'
        ],
        criteria=[
            ['source.repository', 'is', pullrequest_hook_open_data['repository']['name']],
            ['source.number', 'is', pullrequest_hook_open_data['number']]
        ],
        actions=[
            {
                'name': 'get_one',
                'action': 'dummy_action'
            }
        ]
    )
    request = mock.Mock()
    request.data = pullrequest_hook_open_data
    request.META = {'HTTP_X_GITHUB_EVENT': 'pull_request'}

    task_results = handle_github_events(request)

    assert len(task_results) == 1
    build_context = task_results[0].get()
    assert 'get_one' in build_context.results.keys()
    assert build_context.results['get_one'] == 'dummy'





