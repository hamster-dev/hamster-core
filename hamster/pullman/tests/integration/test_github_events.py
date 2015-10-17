import pytest
import os
from unittest import mock

from pullman.events import (
    GithubWebhookPullEvent, PullRequestEvent, PullRequestIssueCommentEvent, CommitStatusEvent
)

def test_event_matching_pullrequest(pullrequest_hook_open_data):
    """Test pull request open webhook deserializes to a pullrequest event."""
    request = mock.Mock()
    request.data = pullrequest_hook_open_data
    request.META = {'HTTP_X_GITHUB_EVENT': 'pull_request'}
    events = GithubWebhookPullEvent.find_matching(
        request
    )
    assert len(events) == 1
    assert isinstance(events[0], PullRequestEvent)
    assert events[0].name == 'pull_request.opened'
    assert type(events[0].data['source']).__name__ == 'PullRequest'
    assert events[0].data['source'].number == pullrequest_hook_open_data['number']
    assert events[0].data['source'].repository == pullrequest_hook_open_data['repository']['name']
    assert events[0].data['source'].mergeable == pullrequest_hook_open_data['pull_request']['mergeable']
    assert len(events[0].data.keys()) == 1


@pytest.mark.skipif(
    not 'HAMSTER_GITHUB_API_TOKEN' in os.environ.keys(),
    reason='This test makes a webservice call that needs ot be mocked')
def test_event_matching_prbuilder(pullrequestcomment_hook_prbuilder_success_data):
    """Test prbuilder status webhook."""
    request = mock.Mock()
    request.data = pullrequestcomment_hook_prbuilder_success_data
    request.META = {'HTTP_X_GITHUB_EVENT': 'issue_comment'}

    events = GithubWebhookPullEvent.find_matching(
        request
    )
    assert len(events) == 2
    assert isinstance(events[0], PullRequestIssueCommentEvent)

    event = events[0]
    assert event.name == 'prbuilder_status.succeeded'
    assert event.data['build_url'] == 'http://jenkins.somewhere/job/some-build/926/'
    assert event.data['build_status'] == 'succeeded'
    assert event.data['build_number'] == '926'
    assert event.data['build_job'] == 'some-build'


@pytest.mark.skipif(
    not 'HAMSTER_GITHUB_API_TOKEN' in os.environ.keys(),
    reason='This test makes a webservice call that needs ot be mocked')
def test_event_matching_commit_status(commit_status_hook_success_data):
    """Test prbuilder status webhook."""
    request = mock.Mock()
    request.data = commit_status_hook_success_data
    request.META = {'HTTP_X_GITHUB_EVENT': 'status'}

    events = GithubWebhookPullEvent.find_matching(
        request
    )
    assert len(events) == 1
    assert isinstance(events[0], CommitStatusEvent)

    event = events[0]
    assert event.name == 'commit_status.success'
    assert type(event.data['source']).__name__ == 'PullRequest'
    assert event.data['source'].repository[1] == commit_status_hook_success_data['repository']['name']
    assert 'status' in event.data
    assert event.data['status'].id == commit_status_hook_success_data['id']
    assert event.data['status'].state == commit_status_hook_success_data['state']
    assert event.data['status'].target_url == commit_status_hook_success_data['target_url']
    assert event.data['status'].context == commit_status_hook_success_data['context']
    assert event.data['status'].sha == commit_status_hook_success_data['sha']



@pytest.mark.skipif(
    not 'HAMSTER_GITHUB_API_TOKEN' in os.environ.keys(),
    reason='This test makes a webservice call that needs ot be mocked')
def test_event_matching_pullrequest_comment(pullrequestcomment_hook_create_data):
    """Test issue comment webhook deserializes to a pullrequestcomment event."""

    request = mock.Mock()
    request.data = pullrequestcomment_hook_create_data
    request.META = {'HTTP_X_GITHUB_EVENT': 'issue_comment'}

    events = GithubWebhookPullEvent.find_matching(
        request
    )
    assert len(events) == 1
    assert isinstance(events[0], PullRequestIssueCommentEvent)
    assert events[0].name == 'pull_request_comment.created'
    assert type(events[0].data['source']).__name__ == 'PullRequest'
    assert events[0].data['source'].number == pullrequestcomment_hook_create_data['issue']['number']
    assert events[0].data['source'].repository == pullrequestcomment_hook_create_data['repository']['name']

    assert len(events[0].data.keys()) == 2
    assert type(events[0].data['comment']).__name__ == 'IssueComment'
    assert events[0].data['comment'].body == 'This is a comment.'
