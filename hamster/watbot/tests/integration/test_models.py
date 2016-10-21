import pytest
import unittest

from django.core.exceptions import ValidationError

from core.event import Event
from core.models import (
    EventSubscriber,
    )
from core.pipeline import Task, TaskArgument, Pipeline
from core.bot import Bot


def test_criteria_prop(db):
    """Test that criteria is unpacked properly.
    """
    event_subscriber_spec = """
    subscriber:
      criteria:
        - 
            - lastname 
            - is 
            - waters
    """

    EventSubscriber.objects.create(data=event_subscriber_spec)
    sub = EventSubscriber.objects.all()[0]
    assert sub.criteria == [['lastname', 'is', 'waters']]


@unittest.skip('might not need this feature')
def test_criteria_prop_error(db):
    """Test that unsupported operator blows up.
    """
    event_subscriber_spec = """
    subscriber:
      criteria:
        - 
            - lastname 
            - is not 
            - waters
    """

    sub = EventSubscriber.objects.create(data=event_subscriber_spec)
    with pytest.raises(ValidationError):
        sub.full_clean()


def test_pipeline_obj_with_args(db):
    """Test that a Pipeline object is created from YAML.
    """
    pipeline_spec = """
    pipeline:
      - some_task:
          pr: lazy=event.pr
          message: template=hello {{ event.pr.user }}
    """
    EventSubscriber.objects.create(data=pipeline_spec)
    sub = EventSubscriber.objects.all()[0]
    assert isinstance(sub.pipeline, Pipeline)
    assert len(sub.pipeline.tasks) == 1


def test_pipeline_obj_no_args(db):
    """Test that a Pipeline object is created from YAML.
    """
    pipeline_spec = """
    pipeline:
      - task_one
    """

    EventSubscriber.objects.create(data=pipeline_spec)
    sub = EventSubscriber.objects.all()[0]
    assert isinstance(sub.pipeline, Pipeline)
    assert len(sub.pipeline.tasks) == 1


def test_subscriber_match(db):
    """Test that event subscribers are idnetified when subscribibg event fires.
    """
    class FooEvent(Event):
        __id = 'foo_event'

    evt = FooEvent(None)
    evt.data = {'lastname': 'waters'}

    event_subscriber_spec = """
    subscriber:
      events:
        - foo_event
      criteria:
        - 
            - lastname 
            - is 
            - waters
    """

    sub = EventSubscriber.objects.create(data=event_subscriber_spec)

    s = EventSubscriber.objects.matching_event(evt)
    assert len(s) == 1
    assert s[0] == sub


class TestBot(Bot):
    __id = 'testbot'
    test = ''
    @property
    def tasks(self):
        return [
            Task(
                'echo',
                [
                    TaskArgument('arg', 'hello')
                ]
            )
        ]


def test_bot_with_args(db):
    """Test that a Pipeline object is created from YAML.
    """
    pipeline_spec = """
    bot:
        name: testbot
        args:
            test: hello
    """
    EventSubscriber.objects.create(data=pipeline_spec)
    sub = EventSubscriber.objects.all()[0]
    assert isinstance(sub.pipeline, Pipeline)
    assert len(sub.pipeline.tasks) == 1


def test_bot_no_args(db):
    """Test that a Pipeline object is created from YAML.
    """
    pipeline_spec = """
    bot:
        name: testbot
    """

    EventSubscriber.objects.create(data=pipeline_spec)
    sub = EventSubscriber.objects.all()[0]
    assert isinstance(sub.pipeline, Pipeline)
    assert len(sub.pipeline.tasks) == 1
