import pytest

from pipeline.actions import TaskAction
from pipeline.context import BuildContext

from pullman.sources import PullRequest

@pytest.mark.skipif(
    True,
    reason='Test requires a webservice call, need to rewrite with mock'
)
def test_pull_request_comment():
    """Test that the pull_request_comment action works correctly."""

    task_action = TaskAction(
        'pull_request_comment',
        name='test_comment',
        message='hello'
    )
    source = PullRequest(
        owner='mike',
        repository='hamster-ci',
        number=2,
        user='freddymergatroid'
    )
    ret = task_action.prepare(source, BuildContext()).apply_async().get()
    assert ret.results['test_comment'] is True

