"""Tests for the github_api overrides to ``pipeline.event.Event``,
specifically the system of matching github webhook metadata to GithubEvent
subclasses using the declarative style.
Event data is not considered, since this uses standard event matching that
is tested in the pipeline module.
"""
import pytest
try:
    import mock
except ImportError:
    from unittest import mock

from github_api.events import (
    GithubEvent, PullRequestEvent, PullRequestIssueCommentEvent,
)


def test_event_matching_pullrequest(monkeypatch):
    """Test eventmatching for pull_request."""
    hook = 'pull_request'
    good_actions = [
        'opened', 'synchronize', 'closed', 'labeled', 'assigned', 'reopened'
    ]
    bad_actions = ['nope']
    monkeypatch.setattr(PullRequestEvent, '_is_relevant', lambda self: True)

    for action in good_actions:
        data = {
            'action': action
        }
        events = GithubEvent.find_matching(data, hook)
        assert len(events) == 1
        assert isinstance(events[0], PullRequestEvent)

    for action in bad_actions:
        data = {
            'action': action
        }
        events = GithubEvent.find_matching(data, hook)
        assert len(events) == 0


def test_event_matching_pr_comment(monkeypatch):
    """Test eventmatching for issue comment."""
    hook = 'issue_comment'
    good_actions = [
        'created'
    ]
    bad_actions = ['nope']
    monkeypatch.setattr(PullRequestIssueCommentEvent, '_is_relevant', lambda self: True)

    with mock.patch.object(PullRequestIssueCommentEvent, 'comment') as mock_comment:
        mock_comment.body = 'comment body'
        for action in good_actions:
            data = {
                'action': action,
                'issue': {'pull_request': 'qwerty'}
            }

            events = GithubEvent.find_matching(data, hook)
            assert len(events) == 1
            assert 'pull_request_comment.created' in [e.name for e in events]


    for action in bad_actions:
        data = {
            'action': action
        }
        events = GithubEvent.find_matching(data, hook)
        assert len(events) == 0


def test_event_matching_jenkins_comment_success(monkeypatch):
    """Test eventmatching for jenkins status comment."""
    hook = 'issue_comment'
    good_actions = [
        'created'
    ]
    monkeypatch.setattr(PullRequestIssueCommentEvent, '_is_relevant', lambda self: True)

    with mock.patch.object(PullRequestIssueCommentEvent, 'comment') as mock_comment:
        mock_comment.body = 'Test PASSed http://yahoo.com'
        for action in good_actions:
            data = {
                'action': action,
                'issue': {'pull_request': 'qwerty'}
            }

            events = GithubEvent.find_matching(data, hook)
            assert len(events) == 2
            assert 'prbuilder_status.succeeded' in [e.name for e in events]


def test_event_matching_jenkins_comment_failed(monkeypatch):
    """Test eventmatching for jenkins status comment."""
    hook = 'issue_comment'
    good_actions = [
        'created'
    ]
    monkeypatch.setattr(PullRequestIssueCommentEvent, '_is_relevant', lambda self: True)

    with mock.patch.object(PullRequestIssueCommentEvent, 'comment') as mock_comment:
        mock_comment.body = 'Test FAILed http://yahoo.com'
        for action in good_actions:
            data = {
                'action': action,
                'issue': {'pull_request': 'qwerty'}
            }

            events = GithubEvent.find_matching(data, hook)
            assert len(events) == 2
            assert 'prbuilder_status.failed' in [e.name for e in events]
