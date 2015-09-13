from github3.issues.comment import IssueComment
from pipeline.actions import action
from .utils import github

import logging
logger = logging.getLogger(__name__)


@action
def pull_request_comment(self, source, message):
    """Make a pull request comment.
    Params:
        source: a PullRequest source
        message - The body of the comment

    """
    assert message, 'template is required for pull request comment'

    _log = "{}/{}/{}".format(source.owner, source.repository, source.number)

    rendered = "<!--HAMSTERED-->\n{}".format(message)

    logger.debug('attempting to comment {} for {}'.format(rendered, _log))

    # this will raise a GithubError if there is an issue, let it propagate
    gh = github()

    # using Issue object, since PR is internally an Issue
    # only way to get a comment on the PR that isnt tied to a change or a commit.
    pr = gh.issue(source.owner, source.repository, source.number)

    if not pr:
        raise ValueError(
            "Cannot make a comment on non-existent pr {}".format(_log)
        )

    ic = pr.create_comment(rendered)

    if not ic or not isinstance(ic, IssueComment):
        #FIXME
        raise Exception(
            "Error creating comment for {}".format(_log)
        )

    logger.info('Created pr comment for {}'.format(_log))

    return True
