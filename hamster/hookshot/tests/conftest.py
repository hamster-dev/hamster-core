"""
conftest.py

py.test hook file
"""
import os
import json
import pytest
from github3.pulls import PullRequest

FIXTURES_BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures')


@pytest.fixture
def object_pullrequest():
    """Returns a PulRequest object
    """
    pth = os.path.join(
        FIXTURES_BASE,
        'objects', 'pullrequest.json'
    )
    with open(pth, 'r') as fh:
        data = fh.read()

    return PullRequest(json.loads(data))


@pytest.fixture
def webhook_pullrequest_opened():
    """Returns a json string for pr open webhook
    """
    pth = os.path.join(
        FIXTURES_BASE,
        'webhooks', 'pull_request.opened.json'
    )
    with open(pth, 'r') as fh:
        data = fh.read()

    return json.loads(data)


@pytest.fixture
def webhook_pullrequestcomment_created():
    """Returns a json string for pullrequest issue comment webhook
    """
    pth = os.path.join(
        FIXTURES_BASE,
        'webhooks', 'issue_comment.created.json'
    )
    with open(pth, 'r') as fh:
        data = fh.read()

    return json.loads(data)


@pytest.fixture
def webhook_pullrequestcomment_prbuilder_success():
    """Returns a json string for pullrequest issue comment webhook
    """
    pth = os.path.join(
        FIXTURES_BASE,
        'webhooks', 'prbuilder_status.succeeded.json'
    )
    with open(pth, 'r') as fh:
        data = fh.read()

    return json.loads(data)


@pytest.fixture
def webhook_commit_status_success():
    """Returns a json string for commit status of success
    """
    pth = os.path.join(
        FIXTURES_BASE,
        'webhooks', 'commit_status.success.json'
    )
    with open(pth, 'r') as fh:
        data = fh.read()

    return json.loads(data)
