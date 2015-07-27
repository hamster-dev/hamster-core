import pytest

from pipeline.event import Event

from pipeline_django.models import PipelineEventHandler

@pytest.fixture
def event_handlers(db):

    PipelineEventHandler.objects.create(
        name="test_one",
        events=[
            'nothing.happened'
        ],
        criteria=[
            ['source.number', 'is', 42],
        ],
        actions=[
            {
                'name': 'get_one',
                'action': 'dummy_action'
            }
        ]
    )

    PipelineEventHandler.objects.create(
        name="test_two",
        events=[
            'something.happened'
        ],
        # criteria=[
        #     ['source.number', 'is', 42],
        # ],
        actions=[
            {
                'name': 'get_one',
                'action': 'shell_command',
                'workspace': 'python',
                'kwargs': {
                    'commands': [
                        'pip install -y flake8-diff',
                        'echo {{ source.number }}'
                    ]
                }
            }
        ]
    )

class NothingEvent(Event):
    __id = 'nothing.happened'
    @property
    def source(self):
        return self._input_data

class SomethingEvent(NothingEvent):
    __id = 'something.happened'


class DummySource(object):
    number = 42

def test_eventhandler_execution(db):
    """Test that an event handler is executed."""
    PipelineEventHandler.objects.create(
        name="test_one",
        events=[
            'nothing.happened'
        ],
        criteria=[
            ['source.number', 'is', 42],
        ],
        actions=[
            {
                'name': 'get_one',
                'action': 'dummy_action'
            }
        ]
    )
    results = PipelineEventHandler.handle_events(Event, DummySource)
    assert len(results) == 1
    result = results[0].get()
    assert result.results['get_one'] == 1


def test_eventhandler_shell_execution(db):
    """Test that an event handler is executed that runs some shell commands."""
    PipelineEventHandler.objects.create(
        name="test_two",
        events=[
            'something.happened'
        ],
        actions=[
            {
                'name': 'run_something',
                'action': 'shell_command',
                'workspace': 'python',
                'kwargs': {
                    'commands': [
                        'pip install flake8-diff',
                        'echo {{ source.number }}'
                    ]
                }
            }
        ]
    )
    results = PipelineEventHandler.handle_events(Event, DummySource)
    assert len(results) == 1
    result = results[0].get()
    task_result = result.results['run_something']
    assert len(task_result) == 3
    assert task_result[0][0].startswith('virtualenv')  # its a python workspace...
    assert task_result[1][0] == 'pip install flake8-diff'
    assert task_result[2][0] == 'echo 42'


def test_eventhandler_serialization():
    """Test that models.PipelineEventHandler correctly serializes
    to pipeline.event.EventHandler.
    """

