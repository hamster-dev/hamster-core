from github3.issues.comment import IssueComment
from pipeline.actions import action
from .utils import github

import logging
logger = logging.getLogger(__name__)


def _get_pull_request_as_issue(owner, repository, number):
    """Get the Issue object that represents a pull request.
    """
    # this will raise a GithubError if there is an issue, let it propagate
    gh = github()

    # using Issue object, since PR is internally an Issue
    # only way to get a comment on the PR that isnt tied to a change or a commit.
    pr = gh.issue(owner, repository, number)

    if not pr:
        raise ValueError(
            "Cannot get non-existent pr {}/{}/{}".format(
                owner, repository, number
            )
        )

    return pr


@action
def pull_request_assign(self, source, to_whom):
    """Assign a pull request to a user.
    :param source: A PullRequest
    :param to_whom: a username

    TODO:
        - verify that the user exists
    """
    logger.debug('attempting to assign {} to {}'.format(to_whom, source))

    pr = _get_pull_request_as_issue(source.owner, source.repository, source.number)
    assigned = pr.assign(to_whom)

    if not assigned:
        raise Exception(
            "Error assigning {} to {}".format(to_whom, source)
        )

    logger.info('Assigned {} to {}'.format(to_whom, source))


@action
def pull_request_comment(self, source, message):
    """Make a pull request comment.
    Params:
        source: a PullRequest source
        message - The body of the comment

    """
    assert message, 'template is required for pull request comment'

    rendered = "<!--HAMSTERED-->\n{}".format(message)

    logger.debug('attempting to comment {} for {}'.format(rendered, source))

    pr = _get_pull_request_as_issue(source.owner, source.repository, source.number)
    ic = pr.create_comment(rendered)

    if not ic or not isinstance(ic, IssueComment):
        raise Exception(
            "Error creating comment for {}".format(source)
        )

    logger.info('Created pr comment for {}'.format(source))

    return True
