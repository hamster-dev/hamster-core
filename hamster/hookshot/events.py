"""
Github pull request webhook-specific event registration.
"""
import re

from cached_property import cached_property
from github3.pulls import ReviewComment, PullRequest
from github3.issues.issue import Issue

from core.event import Event
from hookshot.utils import get_pull_at_head
from hookshot.utils import github

import logging
logger = logging.getLogger(__name__)


class GithubWebhookPullEvent(Event):
    """Base class for github pullrequest-related webhook events.

    :attribute hook_event: the github webhook event that
        the subclass should respond to.  required.
    """
    hook_event = None

    @classmethod
    def matches_input(cls, event_input):
        """Use the hook event provided in the request to determine
        if a subclass matches the input.
        :param event_input: HttpRequest
        :returns: bool
        """
        if event_input.META.get('HTTP_X_GITHUB_EVENT') == cls.hook_event:
            return True

        return False

    def __str__(self):
        return '{} {}'.format(
            self.hook_event,
            self._event_input.data['action']
        )


#class CommitStatusEvent(GithubWebhookPullEvent):
#    """Commit status webhook.
#    """
#    __id = 'commit_status'
#    hook_event = 'status'
#
#    @property
#    def name(self):
#        """Generate a name like 'commit_status.success'.
#        """
#        base_name = super(CommitStatusEvent, self).name
#        return "{}.{}".format(base_name, self._event_input.data['state'])
#
#    @cached_property
#    def data(self):
#        """Expose a `PullRequest` and a `PullRequestStatus`.
#        """
#        organization = self._event_input.data['repository']['owner']['login']
#        repository = self._event_input.data['repository']['name']
#        sha = self._event_input.data['sha']
#        _id = self._event_input.data['id']
#        context = self._event_input.data['context']
#        state = self._event_input.data['state']
#        target_url = self._event_input.data['target_url']
#        raise RuntimeError('FIXME: use source adapter')
#        return {
#            'source': get_pull_at_head(organization, repository, sha),
#            'status': PullRequestStatus(_id, sha, context, state, target_url)
#        }


class PullRequestEvent(GithubWebhookPullEvent):
    """Pull Request github webhook event.
    """
    __id = 'pull_request'
    hook_event = 'pull_request'

    @cached_property
    def name(self):
        """Generate a name like 'pull_request.opened'
        """
        base_name = super(PullRequestEvent, self).name
        return "{}.{}".format(base_name, self._event_input.data['action'])

    @cached_property
    def data(self):
        """Expose a `PullRequest`.
        """
        return {
            'pr': PullRequest(
                self._event_input.data['pull_request']
            )
        }


class PullRequestIssueCommentEvent(PullRequestEvent):
    """Issue Comment github webhook event.
    Only relevant for pull request comments (which are a variant
    of issue comment); if you want to implement issue comment handling,
    there will need to be some magics to distinguish bnetween the variants.
    """
    __id = 'pull_request_comment'
    hook_event = 'issue_comment'

    @classmethod
    def matches_input(cls, event_input):
        """Only match "pull request" and "issue" comments.
        Don't match comments created by hamster.
        :param input_data: request object
        """
        might_match = super(PullRequestIssueCommentEvent, cls).matches_input(event_input)

        if not might_match:
            return False

        data = event_input.data
        return all((
            'issue' in data,
            'pull_request' in data.get('issue', {}),
            # we use hidden text 'HAMSTERED' so we dont enter into infinite loop
            not data.get('comment', {}).get('body', '').startswith('<!--HAMSTERED-->')
        ))

    @cached_property
    def data(self):
        """Expose a `PullRequest` and an `IssueComment`.
        """
        comment = ReviewComment(self._event_input.data['comment'])
        pr = Issue(
            self._event_input.data['issue'],
            session=github()
        ).pull_request()

        return {
            'pr': pr,
            'comment': comment,
        }


#class JenkinsPrBuilderStatusCommentEvent(PullRequestIssueCommentEvent):
#    """Issue comment event handler specific to Jenkins prbuilder plugin
#    status notifications.
#
#    @deprecated
#
#    This class will be removed in 1.0, superceded by `CommitStatusEvent`.
#    """
#    __id = 'prbuilder_status'
#    url_re = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
#
#    @classmethod
#    def matches_input(cls, event_input):
#        """This class is relevant only if there is an url in the
#        deserialized comment body.
#        :param input_data: request object
#        """
#        might_match = super(JenkinsPrBuilderStatusCommentEvent, cls).matches_input(event_input)
#
#        if not might_match:
#            return False
#
#        data = event_input.data
#        return bool(
#            re.search(cls.url_re, data['comment']['body'])
#        )
#
#    @cached_property
#    def data(self):
#        """Change event data by:
#            - adding jenkins build url
#            - modifying event name
#        """
#        raise RuntimeError('FIXME: use source adapter')
#        _data = super(JenkinsPrBuilderStatusCommentEvent, self).data
#
#        comment_body = self._event_input.data['comment']['body']
#        # s/b guaranteed to return a match; see check in `matches_input`
#        build_url = re.search(self.url_re, comment_body).group(0)
#        build_status = 'succeeded' if comment_body.startswith('Test PASSed') else 'failed'
#
#        try:
#            from urllib.parse import urlparse
#        except ImportError:
#            import urlparse
#        path_parts = urlparse(build_url).path.split('/')
#        build_job, build_number = path_parts[2], path_parts[3]
#
#        _data['build_url'] = build_url
#        _data['build_status'] = build_status
#        _data['build_number'] = build_number
#        _data['build_job'] = build_job
#
#        _id = getattr(self, '_{}__id'.format(self.__class__.__name__))
#        _data['event'] = "{}.{}".format(_id, build_status)
#
#        return _data
#
#    @cached_property
#    def name(self):
#        _id = getattr(self, '_{}__id'.format(self.__class__.__name__))
#        return '{}.{}'.format(_id, self.data['build_status'])


# class PullRequestBotSpeakEvent(PullRequestIssueCommentEvent):
#     """Base impl of a bot, which is an event handler attached to
#     pull request comments.
#     """
#     __abstract = True
#     valid_actions = ['created']
#
#     def _deserialize(self):
#         """Modify event data by:
#             - changing event name
#         """
#         data = super(PullRequestBotSpeakEvent, self).data
#
#         _id = getattr(self, '_{}__id'.format(self.__class__.__name__))
#         data['event'] = "{}.speak".format(_id)
#
#         return data


