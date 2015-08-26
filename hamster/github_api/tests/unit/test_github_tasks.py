try:
    import mock
except ImportError:
    from unittest import mock
import pytest

from github3.issues import Issue
from github3.issues.comment import IssueComment

from pipeline.actions import TaskAction
from pipeline.executor import Executor

from github_api.sources import PullRequest


def test_pullrequest_comment_no_pull_request(mocker, pullrequest_hook_open_data):
    """Test that the pr comment task fails when the pull request is invalid."""
    mock_github = mocker.patch('github_api.tasks.github')
    mock_github.return_value.issue.return_value = None

    configuration = {
        'action': 'pull_request_comment',
        'kwargs': {
            'message': 'hello'
        }
    }
    action = TaskAction.from_dict(configuration)
    async_result = Executor().schedule(
        [action],
        PullRequest.from_webhook(pullrequest_hook_open_data)
    )

    with pytest.raises(ValueError):
        async_result.get()


def test_pullrequest_comment_error_create(mocker, pullrequest_hook_open_data):
    """Test that the pr comment task fails when the comment fails."""
    mock_github = mocker.patch('github_api.tasks.github')
    mock_github.return_value.issue.return_value.create_comment.return_value = None

    configuration = {
        'action': 'pull_request_comment',
        'kwargs': {
            'message': 'hello'
        }
    }
    action = TaskAction.from_dict(configuration)
    async_result = Executor().schedule(
        [action],
        PullRequest.from_webhook(pullrequest_hook_open_data)
    )

    with pytest.raises(Exception):
        async_result.get()

def test_pullrequest_comment_ok(mocker, pullrequest_hook_open_data):
    """Test that the pr comment task succeeds."""
    mock_github = mocker.patch('github_api.tasks.github')
    mock_issue = mock.Mock(spec=Issue)  # pullrequest is an issue yadda yadda
    mock_github.return_value.issue.return_value = mock_issue

    mock_comment = mock.MagicMock(spec=IssueComment)
    mock_issue.create_comment.return_value = mock_comment

    configuration = {
        'action': 'pull_request_comment',
        'kwargs': {
            'message': 'hello'
        }
    }
    pullrequest = PullRequest.from_webhook(pullrequest_hook_open_data)
    action = TaskAction.from_dict(configuration)
    async_result = Executor().schedule([action], pullrequest)
    async_result.get()

    mock_github.return_value.issue.assert_called_with(
        pullrequest.owner, pullrequest.repository, pullrequest.number
    )
    mock_issue.create_comment.assert_called_with("<!--HAMSTERED-->\nhello")


def test_pullrequest_comment_ok_template(mocker, pullrequest_hook_open_data):
    """Test that the pr comment task with a template succeeds."""
    mock_github = mocker.patch('github_api.tasks.github')
    mock_issue = mock.Mock(spec=Issue)  # pullrequest is an issue yadda yadda
    mock_github.return_value.issue.return_value = mock_issue

    mock_comment = mock.MagicMock(spec=IssueComment)
    mock_issue.create_comment.return_value = mock_comment

    configuration = {
        'action': 'pull_request_comment',
        'kwargs': {
            'message': '{{ source.number }}'
        }
    }
    pullrequest = PullRequest.from_webhook(pullrequest_hook_open_data)
    action = TaskAction.from_dict(configuration)
    async_result = Executor().schedule([action], pullrequest)
    async_result.get()

    mock_github.return_value.issue.assert_called_with(
        pullrequest.owner, pullrequest.repository, pullrequest.number
    )
    mock_issue.create_comment.assert_called_with("<!--HAMSTERED-->\n5")

