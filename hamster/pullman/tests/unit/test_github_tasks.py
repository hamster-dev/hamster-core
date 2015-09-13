try:
    import mock
except ImportError:
    from unittest import mock
import pytest

from github3.issues import Issue
from github3.issues.comment import IssueComment

from pipeline.actions import TaskAction
from pipeline import BuildContext


def test_pullrequest_comment_no_pull_request(mocker, pullrequest_object):
    """Test that the pr comment task fails when the pull request is invalid."""
    mock_github = mocker.patch('pullman.tasks.github')
    mock_github.return_value.issue.return_value = None

    action = TaskAction('pull_request_comment', message='hello')
    partial = action.prepare(pullrequest_object, BuildContext())
    async_result = partial.delay()

    with pytest.raises(ValueError):
        async_result.get()


def test_pullrequest_comment_error_create(mocker, pullrequest_object):
    """Test that the pr comment task fails when the comment fails."""
    mock_github = mocker.patch('pullman.tasks.github')
    mock_github.return_value.issue.return_value.create_comment.return_value = None

    action = TaskAction('pull_request_comment', message='hello')
    partial = action.prepare(pullrequest_object, BuildContext())
    async_result = partial.delay()

    with pytest.raises(Exception):
        async_result.get()

def test_pullrequest_comment_ok(mocker, pullrequest_object):
    """Test that the pr comment task succeeds."""
    mock_github = mocker.patch('pullman.tasks.github')
    mock_issue = mock.Mock(spec=Issue)  # pullrequest is an issue yadda yadda
    mock_github.return_value.issue.return_value = mock_issue

    mock_comment = mock.MagicMock(spec=IssueComment)
    mock_issue.create_comment.return_value = mock_comment

    action = TaskAction('pull_request_comment', message='hello')
    partial = action.prepare(pullrequest_object, BuildContext())
    partial.delay().get()

    mock_github.return_value.issue.assert_called_with(
        pullrequest_object.owner, pullrequest_object.repository, pullrequest_object.number
    )
    mock_issue.create_comment.assert_called_with("<!--HAMSTERED-->\nhello")


def test_pullrequest_comment_ok_template(mocker, pullrequest_object):
    """Test that the pr comment task with a template succeeds."""
    mock_github = mocker.patch('pullman.tasks.github')
    mock_issue = mock.Mock(spec=Issue)  # pullrequest is an issue yadda yadda
    mock_github.return_value.issue.return_value = mock_issue

    mock_comment = mock.MagicMock(spec=IssueComment)
    mock_issue.create_comment.return_value = mock_comment



    action = TaskAction('pull_request_comment', message='hello')
    partial = action.prepare(pullrequest_object, BuildContext())
    partial.delay().get()

    mock_github.return_value.issue.assert_called_with(
        pullrequest_object.owner, pullrequest_object.repository, pullrequest_object.number
    )
    mock_issue.create_comment.assert_called_with("<!--HAMSTERED-->\nhello")

