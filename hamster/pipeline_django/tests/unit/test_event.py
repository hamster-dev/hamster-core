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
        return self._event_input

class Foo2Event(FooEvent):
    __id = 'foo2_event'
    criteria = [
        ('foo', 'is', 42),
        ('bar', 'in', [1,2,3])
    ]

@pytest.mark.xfail(reason='feature has been removed')
def test_single_criteria_match_success():
    """Test that an event's criteria matches input
    """
    events = CriteriaEvent.find_matching({'foo': 42})
    assert len(events) == 1
    assert events[0].name == 'foo_event'

@pytest.mark.xfail(reason='feature has been removed')
def test_multiple_criteria_match_success():
    """Test that an event's criteria matches input
    """
    events = CriteriaEvent.find_matching({'foo': 42, 'bar': 1})
    assert len(events) == 2
    assert 'foo2_event' in [e.name for e in events]


