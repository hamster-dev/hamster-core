import pytest

from pipeline_django.event import Event


class CriteriaEvent(Event):
    """This is just used to scope the event search space to this module,
    so that events from other modules dont leak in."""
    pass

class FooEvent(CriteriaEvent):
    __id = 'foo_event'
    criteria = [('foo', 'is', 42)]


    @property
    def data(self):
        """Simple deserializer that just returns the input data as-is
        """
        return self._input_data

class Foo2Event(FooEvent):
    __id = 'foo2_event'
    criteria = [
        ('foo', 'is', 42),
        ('bar', 'in', [1,2,3])
    ]


def test_single_criteria_match_success():
    """Test that an event's criteria matches input
    """
    events = CriteriaEvent.find_matching({'foo': 42})
    assert len(events) == 1
    assert events[0].name == 'foo_event'

def test_multiple_criteria_match_success():
    """Test that an event's criteria matches input
    """
    events = CriteriaEvent.find_matching({'foo': 42, 'bar': 1})
    assert len(events) == 2
    assert 'foo2_event' in [e.name for e in events]


class BarEvent(Event):
    __id = 'bar_event'
    @property
    def source(self):

        return self._input_data['thesource']

def test_event_data():
    """Test that event data is correctly deserialized
    """


    bar = BarEvent({
        'thesource': 1234
    })
    assert bar.data == {
        'source': 1234,
        'event': 'bar_event'
    }
