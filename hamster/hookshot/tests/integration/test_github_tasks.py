from django.conf import settings
from pipeline.pipeline import TaskSpec, schedule

dvd = settings.DVD


def test_pull_request_label(object_pullrequest):
    """Test that a pull request assignment task is executed and an issue is assigned.
    """
    spec = TaskSpec(
        'pull_request_label',
        'pr_result',
        kwargs=dict(pr=object_pullrequest, label='bug'),
    )
    with dvd.use_cassette('pr-label-mike-hamster-ci-2.yaml'):
        result = schedule([spec]).get()
        # `result` will be a `pipeline.state.StateTracker` instance
        # with our return value as it's pr_result property
        assert result.pr_result is True


def test_pull_request_assign(object_pullrequest):
    """Test that a pull request assignment task is executed and an issue is assigned.
    """
    spec = TaskSpec(
        'pull_request_assign',
        'pr_result',
        kwargs=dict(pr=object_pullrequest, to_whom='mikewaters'),
    )
    with dvd.use_cassette('pr-assign-mike-hamster-ci-2.yaml'):
        result = schedule([spec]).get()
        # `result` will be a `pipeline.state.StateTracker` instance
        # with our return value as it's pr_result property
        assert result.pr_result is True


def test_pull_request_comment(object_pullrequest):
    """Test that a pull request comment is executed and a comment is emitted.
    """
    spec = TaskSpec(
        'pull_request_comment',
        'pr_result',
        kwargs=dict(pr=object_pullrequest, message='hello'),
    )
    with dvd.use_cassette('pr-comment-mike-hamster-ci-2.yaml'):
        result = schedule([spec]).get()
        # `result` will be a `pipeline.state.StateTracker` instance
        # with our return value as it's pr_result property
        assert result.pr_result is True


def test_pull_request_status(object_pullrequest):
    """Test that a pull request status task is called and completes.
    """
    spec = TaskSpec(
        'pull_request_status',
        'pr_result',
        kwargs=dict(pr=object_pullrequest, state='pending'),
    )
    with dvd.use_cassette('pr-status-mike-hamster-ci-2.yaml'):
        result = schedule([spec]).get()
        assert result.pr_result is True
