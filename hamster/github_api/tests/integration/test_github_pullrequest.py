import pytest

from github_api.sources import PullRequest


@pytest.mark.xfail(reason='This test requires a web service call, need to replace with a mock')
def test_create_from_issue_comment(pullrequestcomment_hook_create_data):
    """Test that a pull request is created from issue comment."""
    pr = PullRequest.from_webhook(pullrequestcomment_hook_create_data)
    assert type(pr).__name__ == 'PullRequest'


def test_create_from_pullrequest(pullrequest_hook_open_data):
    """Test that a pull request is created from issue comment."""
    pr = PullRequest.from_webhook(pullrequest_hook_open_data)
    assert type(pr).__name__ == 'PullRequest'
