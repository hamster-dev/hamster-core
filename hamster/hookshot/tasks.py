from github3.issues.comment import IssueComment
from github3.repos.status import Status
from pipeline.pipeline import state_aware_task
from .utils import github, refresh_session

import logging
logger = logging.getLogger(__name__)


def _get_pull_request_as_issue(owner, repository, number):
    """Get the Issue object that represents a pull request.
    """
    # this will raise a GithubError if there is an issue, let it propagate
    gh = github()

    # using Issue object, since PR is internally an Issue
    # only way to get a comment on the PR that isnt tied to
    # a change or a commit.
    pr = gh.issue(owner, repository, number)

    if not pr:
        raise ValueError(
            "Cannot get non-existent pr {}/{}/{}".format(
                owner, repository, number
            )
        )

    return pr


@state_aware_task
def pull_request_label(pr, label):
    """Label a PR.
    :param source: A PullRequest
    :param labels (str): labels to assign
    :returns: bool

    TODO:
        - verify that the user exists
    """
    refresh_session(pr)
    logger.debug('attempting to label {} using {}'.format(pr, label))

    issue = _get_pull_request_as_issue(
        pr.repository[0].split('/')[-1],
        pr.repository[1],
        pr.number
    )
    labels = issue.add_labels(*[label])

    if not labels:
        raise Exception(
            "Error labeling {} using {}".format(pr, label)
        )

    logger.info('Labeled {} with {}'.format(pr, label))

    return True


@state_aware_task
def pull_request_assign(pr, to_whom):
    """Assign a pull request to a user.
    :param pr: A PullRequest
    :param to_whom: a username
    :returns: bool
    Supports GH 2.6 only (multiple asisgnees are not supported)
    TODO:
        - verify that the user exists
    """
    refresh_session(pr)
    logger.debug('attempting to assign {} to {}'.format(to_whom, pr))

    issue = _get_pull_request_as_issue(
        pr.repository[0].split('/')[-1],
        pr.repository[1],
        pr.number
    )
    assigned = issue.assign(to_whom)

    if not assigned:
        raise Exception(
            "Error assigning {} to {}".format(to_whom, pr)
        )

    logger.info('Assigned {} to {}'.format(to_whom, pr))

    return True


@state_aware_task
def pull_request_comment(pr, message):
    """Make a pull request comment.
    Params:
        pr: a PullRequest pr
        message - The body of the comment

    :returns: bool
    """
    import pdb; pdb.set_trace()
    refresh_session(pr)
    assert message, 'template is required for pull request comment'

    rendered = "<!--HAMSTERED-->\n{}".format(message)

    logger.debug('attempting to comment {} for {}'.format(rendered, pr))

    # in order to create a comment on the pr 'conversation' page,
    # we need to get the Issue object that corresponds to the PullRequest.
    pr = _get_pull_request_as_issue(
        pr.repository[0].split('/')[-1],
        pr.repository[1],
        pr.number
    )
    ic = pr.create_comment(rendered)

    if not ic or not isinstance(ic, IssueComment):
        raise Exception(
            "Error creating comment for {}".format(pr)
        )

    logger.info('Created pr comment for {}'.format(pr))

    return True


@state_aware_task
def pull_request_status(pr, state, target_url=None, description=None, context='hamster'):
    """Create a commit status on the HEAD of a pull request.
    Params:
        pr: a PullRequest pr
        state (str): commit state, ‘pending’, ‘success’, ‘error’, ‘failure’
        target_url (str): optional url for the status
        description (str): optional short description
        context (str): optional status identifier

    :returns: bool
    """
    refresh_session(pr)
    logger.debug('attempting to create commit status {} for {}'.format(state, pr))

    # for some reason, commit status is at the repository level,
    # AND, github3.py `PullRequest.repository` property is a tuple
    # instead of a `Repository` instance, so we need to do this
    # crapola instead of reading from the object passed into this func.
    gh = github()
    repo = gh.repository(pr.repository[0].split('/')[-1], pr.repository[1])

    status = repo.create_status(
        pr.head.sha, state,
        target_url=target_url, description=description, context=context
    )

    if not status or not isinstance(status, Status):
        raise Exception(
            "Error creating commit status for {}".format(pr)
        )

    logger.info('Created commit status for {}'.format(pr))

    return True
