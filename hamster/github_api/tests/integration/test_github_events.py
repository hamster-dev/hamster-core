import pytest

from github_api.events import (
    GithubEvent, PullRequestEvent, PullRequestIssueCommentEvent,
)

def test_event_matching_pullrequest(pullrequest_hook_open_data):
    """Test pull request open webhook deserializes to a pullrequest event."""
    request_data = pullrequest_hook_open_data
    event_type = 'pull_request'
    events = GithubEvent.find_relevant(
        request_data, event_type
    )
    assert len(events) == 1
    assert isinstance(events[0], PullRequestEvent)
    assert events[0].name == 'pull_request.opened'
    assert events[0].action == request_data['action']
    assert type(events[0].source).__name__ == 'PullRequest'
    assert events[0].source.number == request_data['number']
    assert events[0].source.repository == request_data['repository']['name']
    assert events[0].source.mergeable == request_data['pull_request']['mergeable']
    assert len(events[0].data.keys()) == 2
    assert events[0].data['event'] == events[0].name
    assert events[0].data['source'] == events[0].source


@pytest.mark.xfail(reason='This test makes a webservice call that needs ot be mocked')
def test_event_matching_pullrequest_comment(pullrequestcomment_hook_create_data):
    """Test issue comment webhook deserializes to a pullrequestcomment event."""
    request_data = pullrequestcomment_hook_create_data
    event_type = 'issue_comment'
    events = GithubEvent.find_relevant(
        request_data, event_type
    )
    assert len(events) == 1
    assert isinstance(events[0], PullRequestIssueCommentEvent)
    assert events[0].name == 'pull_request_comment.created'
    assert events[0].action == request_data['action']
    assert type(events[0].source).__name__ == 'PullRequest'
    assert events[0].source.number == 6
    assert events[0].source.repository == 'hamster-ci'
    assert events[0].source.mergeable == True
    assert len(events[0].data.keys()) == 3
    assert events[0].data['event'] == events[0].name
    assert events[0].data['source'] == events[0].source
    assert hasattr(events[0], 'comment')
    assert events[0].data['comment'] == events[0].comment
    assert type(events[0].comment).__name__ == 'IssueComment'
    assert events[0].comment.body == 'HELLO'
