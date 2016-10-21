"""
Tests for hookshot-specific subclasses of `event.event.Event`
"""
import pytest
from unittest import mock

from hookshot.events import (
    GithubWebhookPullEvent, PullRequestEvent, PullRequestIssueCommentEvent
)

from core.event import Event
from core.models import (
    EventSubscriber,
    )

from core.pipeline import TaskArgument, LazyTaskArgument


def test_event_matching_pullrequest(webhook_pullrequest_opened):
    """Test pull request open webhook deserializes to a pullrequest event."""
    request = mock.Mock()
    request.data = webhook_pullrequest_opened
    request.META = {'HTTP_X_GITHUB_EVENT': 'pull_request'}
    events = GithubWebhookPullEvent.find_matching(
        request
    )
    assert len(events) == 1
    assert isinstance(events[0], PullRequestEvent)
    assert events[0].name == 'pull_request.opened'
    assert type(events[0].data['pr']).__name__ == 'PullRequest'
    assert events[0].data['pr'].number == webhook_pullrequest_opened['number']
    assert events[0].data['pr'].repository == ('repos/mikewaters', 'pipeline')
    assert events[0].data['pr'].mergeable == webhook_pullrequest_opened['pull_request']['mergeable']
    assert len(events[0].data.keys()) == 1


@pytest.mark.skipif(
    1 == 1,
    reason='This test makes a webservice call that needs ot be mocked')
def test_event_matching_prbuilder(webhook_pullrequestcomment_prbuilder_success_data):
    """Test prbuilder status webhook."""
    request = mock.Mock()
    request.data = webhook_pullrequestcomment_prbuilder_success_data
    request.META = {'HTTP_X_GITHUB_EVENT': 'issue_comment'}

    events = GithubWebhookPullEvent.find_matching(
        request
    )
    assert len(events) == 1
    assert isinstance(events[0], PullRequestIssueCommentEvent)

    event = events[0]
    assert event.name == 'pull_request_comment.created'
    assert event.data['comment'] == 'http://jenkins.somewhere/job/some-build/926/'


def test_subscriber_match(webhook_pullrequest_opened, db):
    """Test that event subscribers are idnetified when subscribibg event fires.
    """

    request = mock.Mock()
    request.data = webhook_pullrequest_opened
    request.META = {'HTTP_X_GITHUB_EVENT': 'pull_request'}

    events = GithubWebhookPullEvent.find_matching(
        request
    )
    evt = events[0]

    pipeline_spec = """
    subscriber:
        events:
            - pull_request.opened
        criteria:
            -
              - pr.number 
              - is 
              - 1
    """

    sub = EventSubscriber.objects.create(
        data=pipeline_spec
    )

    s = EventSubscriber.objects.matching_event(evt)
    assert len(s) == 1
    assert s[0] == sub


def test_subscribed_pipeline_same_name_eager(webhook_pullrequest_opened, db):
    """Test that a hokshot event fires and data[pr] is passed into a task
    """

    request = mock.Mock()
    request.data = webhook_pullrequest_opened
    request.META = {'HTTP_X_GITHUB_EVENT': 'pull_request'}
    events = GithubWebhookPullEvent.find_matching(
        request
    )
    evt = events[0]

    pipeline_spec = """
    pipeline:
      - a_pull:
          pr: lazy=event.pr
    subscriber:
        events:
            - pull_request.opened
        criteria:
            -
              - pr.number 
              - is 
              - 1
    """

    EventSubscriber.objects.create(
        data=pipeline_spec
    )

    s = EventSubscriber.objects.matching_event(evt)

    ret = s[0].pipeline.run(evt.data).get()

    # pipeline will return a `pipeline.state.StateTracker` instance
    # task passes object through to return value
    assert ret.a_pull == evt.data['pr']
