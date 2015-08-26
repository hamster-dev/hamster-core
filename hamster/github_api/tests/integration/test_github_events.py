import pytest
import os
from unittest import mock

from github_api.events import (
    GithubWebhookEvent, PullRequestEvent, PullRequestIssueCommentEvent,
)

def test_event_matching_pullrequest(pullrequest_hook_open_data):
    """Test pull request open webhook deserializes to a pullrequest event."""
    request = mock.Mock()
    request.data = pullrequest_hook_open_data
    request.META = {'HTTP_X_GITHUB_EVENT': 'pull_request'}

    events = GithubWebhookEvent.find_matching(
        request
    )
    assert len(events) == 1
    assert isinstance(events[0], PullRequestEvent)
    assert events[0].name == 'pull_request.opened'
    assert events[0].action == pullrequest_hook_open_data['action']
    assert type(events[0].source).__name__ == 'PullRequest'
    assert events[0].source.number == pullrequest_hook_open_data['number']
    assert events[0].source.repository == pullrequest_hook_open_data['repository']['name']
    assert events[0].source.mergeable == pullrequest_hook_open_data['pull_request']['mergeable']
    assert len(events[0].data.keys()) == 2
    assert events[0].data['event'] == events[0].name
    assert events[0].data['source'] == events[0].source

@pytest.mark.skipif(
    not 'HAMSTER_GITHUB_API_TOKEN' in os.environ.keys(),
    reason='This test makes a webservice call that needs ot be mocked')
def test_event_matching_prbuilder(pullrequestcomment_hook_prbuilder_success_data):
    """Test prbuilder status webhook."""
    request = mock.Mock()
    request.data = pullrequestcomment_hook_prbuilder_success_data
    request.META = {'HTTP_X_GITHUB_EVENT': 'issue_comment'}

    events = GithubWebhookEvent.find_matching(
        request
    )
    assert len(events) == 2
    assert isinstance(events[0], PullRequestIssueCommentEvent)

    event = events[1]  # will always be second, list s/b ordered by position in class hierarchy
    pytest.set_trace()
    assert event.name == 'prbuilder_status.succeeded'
    assert event.data['build_url'] == event.url == 'http://jenkins.somewhere/job/some-build/926/'
    assert event.data['build_status'] == 'succeeded'
    assert event.data['build_number'] == '926'
    assert event.data['build_job'] == 'some-build'


@pytest.mark.skipif(
    not 'HAMSTER_GITHUB_API_TOKEN' in os.environ.keys(),
    reason='This test makes a webservice call that needs ot be mocked')
def test_event_matching_pullrequest_comment(pullrequestcomment_hook_create_data):
    """Test issue comment webhook deserializes to a pullrequestcomment event."""

    request = mock.Mock()
    request.data = pullrequestcomment_hook_create_data
    request.META = {'HTTP_X_GITHUB_EVENT': 'issue_comment'}

    events = GithubWebhookEvent.find_matching(
        request
    )
    assert len(events) == 1
    assert isinstance(events[0], PullRequestIssueCommentEvent)
    assert events[0].name == 'pull_request_comment.created'
    assert events[0].action == pullrequestcomment_hook_create_data['action']
    assert type(events[0].source).__name__ == 'PullRequest'
    assert events[0].source.number == pullrequestcomment_hook_create_data['issue']['number']
    assert events[0].source.repository == pullrequestcomment_hook_create_data['repository']['name']

    assert len(events[0].data.keys()) == 3
    assert events[0].data['event'] == events[0].name
    assert events[0].data['source'] == events[0].source
    assert hasattr(events[0], 'comment')
    assert events[0].data['comment'] == events[0].comment
    assert type(events[0].comment).__name__ == 'IssueComment'
    assert events[0].comment.body == 'This is a comment.'
