import pytest

from pipeline_django.event import Event
from pipeline_django.models import EventSubscriber, Pipeline


class WhateverEvent(Event):
    """This is just used to scope the event search space to this module,
    so that events from other modules dont leak in."""
    pass


class NothingEvent(WhateverEvent):
    __id = 'nothing.happened'
    @property
    def data(self):
        _data =  super(NothingEvent, self).data
        _data.update({
            'source': self._event_input
        })
        return _data


class SomethingEvent(NothingEvent):
    __id = 'something.happened'


class DummySource(object):
    number = 42


def test_eventsubscriber_execution(db, scoped_broker):
    """Test that an event subscriber is executed."""
    pl = Pipeline.objects.create(
        id=1,
        name="test_one",
        actions=[
            {
                'name': 'get_one',
                'action': 'dummy_action'
            }
        ]
    )
    EventSubscriber.objects.create(
        events=[
            'nothing.happened'
        ],
        criteria=[
            ['source.number', 'is', 42],
        ],
        pipeline=pl
    )
    e = NothingEvent(DummySource())
    subs = [s for s in EventSubscriber.objects.matching_event(e)]
    assert len(subs) == 1
    s = subs[0]
    async_result = s.pipeline.schedule(e.data)
    result = async_result.get()
    assert result.results['get_one'] == 'dummy'


def test_eventsubscriber_execution_with_hooks(db, scoped_broker):
    """Test that an event subscriber is executed."""
    pl = Pipeline.objects.create(
        name="test_one",
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
    EventSubscriber.objects.create(
        events=[
            'nothing.happened'
        ],
        criteria=[
            ['source.number', 'is', 42],
        ],
        pipeline=pl
    )
    e = NothingEvent(DummySource())
    
    subs = [s for s in EventSubscriber.objects.matching_event(e)]
    assert len(subs) == 1
    s = subs[0]
    s.pipeline.schedule(e.data).get()

    from .tasks import increment_call_count
    assert increment_call_count.call_count == 4


def test_eventhandler_shell_execution(db, scoped_broker):
    """Test that an event handler is executed that runs some shell commands."""
    pl = Pipeline.objects.create(
        name="test_two",
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
    EventSubscriber.objects.create(
        events=[
            'something.happened'
        ],
        pipeline=pl
    )
    e = SomethingEvent(DummySource())
    subs = [s for s in EventSubscriber.objects.matching_event(e)]
    assert len(subs) == 1
    s = subs[0]
    result = s.pipeline.schedule(e.data).get()
    task_result = result.results['run_something'].log
    assert len(task_result) == 2
    assert task_result[0][0].startswith('virtualenv')  # its a python workspace...
    assert task_result[1][0] == 'echo 42'

    
def test_eventsubscriber_execution(db, scoped_broker):
    """Test that an event subscriber is executed."""
    pl = Pipeline.objects.create(
        id=1,
        name="test_one",
        actions=[
            {
                'name': 'get_one',
                'action': 'dummy_action'
            }
        ]
    )
    EventSubscriber.objects.create(
        events=[
            'nothing.happened'
        ],
        criteria=[
            ['source.number', 'is', 42],
        ],
        pipeline=pl
    )
    e = NothingEvent(DummySource())
    subs = [s for s in EventSubscriber.objects.matching_event(e)]
    assert len(subs) == 1
    s = subs[0]
    async_result = s.pipeline.schedule(e.data)
    result = async_result.get()
    assert result.results['get_one'] == 'dummy'
