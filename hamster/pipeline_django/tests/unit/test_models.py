import pytest

from pipeline_django.event import Event, EventHandler

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
    def data(self):
        self.source = self._input_data
        return super(NothingEvent, self).data


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
    results = EventHandler.handle_events(Event, DummySource())
    assert len(results) == 1
    result = results[0].get()
    assert result.results['get_one'] == 'dummy'


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
    results = EventHandler.handle_events(Event, DummySource)
    assert len(results) == 1
    result = results[0].get()
    pytest.set_trace()
    task_result = result.results['run_something'].log
    assert len(task_result) == 3
    assert task_result[0][0].startswith('virtualenv')  # its a python workspace...
    assert task_result[1][0] == 'pip install flake8-diff'
    assert task_result[2][0] == 'echo 42'
