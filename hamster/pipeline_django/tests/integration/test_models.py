import pytest

from pipeline_django.event import Event
from pipeline_django.models import PipelineEventHandler


class WhateverEvent(Event):
    """This is just used to scope the event search space to this module,
    so that events from other modules dont leak in."""
    pass


class NothingEvent(WhateverEvent):
    __id = 'nothing.happened'
    @property
    def data(self):
        self.source = self._input_data
        return super(NothingEvent, self).data


class SomethingEvent(NothingEvent):
    __id = 'something.happened'


class DummySource(object):
    number = 42


def test_eventhandler_execution(db, scoped_broker):
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
    events = WhateverEvent.find_matching(DummySource())

    results = PipelineEventHandler.objects.handle_events(events)
    assert len(results) == 1

    result = results[0].get()
    assert result.results['get_one'] == 'dummy'


def test_eventhandler_execution_with_hooks(db, scoped_broker):
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
                'action': 'increment_call_count',
                'hooks': [
                    {
                        'action': 'increment_call_count',
                    },
                    {
                        'action': 'increment_call_count',
                        'event': 'pre'
                    },
                    {
                        'action': 'increment_call_count',
                    },
                ]
            }
        ]
    )
    events = WhateverEvent.find_matching(DummySource())

    PipelineEventHandler.objects.handle_events(events)[0].get()

    from .tasks import increment_call_count
    assert increment_call_count.call_count == 4


def test_eventhandler_shell_execution(db, scoped_broker):
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
                        'echo {{ source.number }}'
                    ]
                }
            }
        ]
    )
    events = WhateverEvent.find_matching(DummySource())
    results = PipelineEventHandler.objects.handle_events(events)

    assert len(results) == 1

    result = results[0].get()
    task_result = result.results['run_something'].log
    assert len(task_result) == 2
    assert task_result[0][0].startswith('virtualenv')  # its a python workspace...
    assert task_result[1][0] == 'echo 42'
