"""
Github webhook-specific event registration.

Requirements:
    - in addition to basic cirteria support in base
    event system, webhook events need to react to the
    data provided in the hook.
    This includes:
        - hook type (pull request etc)
        - hook action (open, etc - specific to hook type)
        - the deserialized data from the hook body
"""
import re

from cached_property import cached_property

from pipeline_django.event import Event
from github_api.sources import IssueComment, PullRequest


class GithubEvent(Event):
    """Base class for github webhook events.

    :attribute hook_event: the github webhook event that
        the subclass should respond to.  required.
    :attribute valid_actions: list of github webhook event actions
        the subclass should respond to.  required.
    """
    hook_event = None
    valid_actions = []

    @classmethod
    def find_relevant(cls, input_data, hook_event_name):
        """Get the event types that listen for a given webhook http request.

        hook_event_name is extracted from http header, so it is not
        available in the input data.

            - find subclasses that listen for provided hook
            - filter by those that listen to the provided hook action
        """
        # find events with a `hook_event` that matches the given hook
        registered_for_hook = Event.find('hook_event', hook_event_name)

        # filter those events by the hook action
        action = input_data.get('action')
        if action:
            registered_for_hook = filter(
                lambda klass: action in klass.valid_actions, registered_for_hook
            )

        # mimic behavior of our base class ny matching
        # event criteria to input data
        found = []
        for klass in registered_for_hook:
            instance = klass(input_data)
            if instance._is_relevant():
                found.append(instance)

        return found

    @cached_property
    def action(self):
        """Extract the hook action from the request data.
        """
        return self._input_data.get('action')

    @cached_property
    def name(self):
        """Override base class impl, allowing for hook 'actions', which
        are more specific instances of a given event.
        e.g. "pull_request.opened"
        """
        base_name = super(GithubEvent, self).name
        return "{}.{}".format(base_name, self.action)

    def __repr__(self):
        #TODO: move to pipeline, in base class
        return "{}/{}/{}".format(self.__class__.__name__, self.name, type(self.source))

class PullRequestEvent(GithubEvent):
    """Pull Request github webhook event.
    """
    __id = 'pull_request'
    hook_event = 'pull_request'
    valid_actions = [
        'opened', 'synchronized', 'closed', 'labeled', 'assigned', 'reopened'
    ]

    @cached_property
    def source(self):
        return PullRequest.from_webhook(
            self._input_data
        )


class PullRequestIssueCommentEvent(GithubEvent):
    """Issue Comment github webhook event.
    Only relevant for pull request comments (which are a variant
    of issue comment); if you want to implement issue comment handling,
    there will need to be some magics to distinguish bnetween the variants.
    """
    __id = 'pull_request_comment'
    hook_event = 'issue_comment'
    valid_actions = ['created']
    criteria = [
        ('comment.body', 'not like', r'^<!--HAMSTERED-->')
    ]

    def _is_relevant(self):
        """In addition to criteria matching, this class is relevant
        only if the input data contains the key 'issue.pull_request'.
        This check is required because the issue_comment hook is
        relevant to both github Issues and github Pull Requests.
        """
        if not 'issue' in self._input_data or \
                not 'pull_request' in self._input_data['issue']:
            return False

        return super(PullRequestIssueCommentEvent, self)._is_relevant()

    @cached_property
    def source(self):
        return PullRequest.from_webhook(
            self._input_data
        )

    @cached_property
    def comment(self):
        return IssueComment(self._input_data['comment'])

    @cached_property
    def data(self):
        data = super(PullRequestIssueCommentEvent, self).data
        data.update({
            'comment': self.comment
        })
        return data


class JenkinsPrBuilderStatusCommentEvent(PullRequestIssueCommentEvent):
    """Issue comment event handler specific to Jenkins prbuilder plugin
    status notifications.
    TODO: Will be moved to jenkins module.
    """
    __id = 'prbuilder_status'

    valid_actions = ['created']
    url_re = r'https?://[^\s<>"]+|www\.[^\s<>"]+'

    criteria = [
        ('comment.body', 'like', r'^Test [PASFIL]{4}ed'),
    ]

    def _is_relevant(self):
        """In addition to the base behavior of criteria matching,
        this class is relevant only if there is an url in the deserialized comment body.
        This is done here, and not in `self.criteria`, because
        if this information is not present, `self.data` will raise
        an exception.
        TODO; figure out a technique to work around this sort of
        chicken-and-egg problem.  pwrhaps use two passes; the first pass
        is run against the input data, and the second pass is run against the
        deserialized data.
        """
        if not re.search(self.url_re, self.comment.body):
            return False

        return super(JenkinsPrBuilderStatusCommentEvent, self)._is_relevant()

    @cached_property
    def data(self):
        """Modify event data by:
            - adding jenkins build url
            - changing event name
        """
        data = super(JenkinsPrBuilderStatusCommentEvent, self).data

        data['build_url'] = self.url
        data['build_status'] = self.build_status
        data['build_number'] = self.build_number
        data['build_job'] = self.build_job

        _id = getattr(self, '_{}__id'.format(self.__class__.__name__))
        data['event'] = "{}.{}".format(_id, self.build_status)

        return data

    @cached_property
    def url(self):
        """Extract build url from the comment.
        Guranteed to match, since we are using the same regex
        that is_relevant uses.
        """
        match = re.search(self.url_re, self.comment.body)
        return match.group(0)

    def _get_build_url_params(self):
        """Get build url params.
        """
        try:
            from urllib.parse import urlparse
        except ImportError:
            import urlparse
        path_parts = urlparse(self.url).path.split('/')
        return path_parts[2], path_parts[3]

    @cached_property
    def build_job(self):
        """Build job name.
        """
        return self._get_build_url_params()[0]

    @cached_property
    def build_number(self):
        """Build job number.
        """
        return self._get_build_url_params()[1]

    @cached_property
    def build_status(self):
        """Return build success/failure status.
        """
        return 'succeeded' if self.comment.body.startswith('Test PASSed') else 'failed'

    @cached_property
    def name(self):
        _id = getattr(self, '_{}__id'.format(self.__class__.__name__))
        return '{}.{}'.format(_id, self.build_status)


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

# class PullRequestReviewCommentEvent(GithubEvent):
#     __id = 'pull_request_review_comment'
#     hook_event = 'pull_request_review_comment'
#     valid_actions = ['created']
#
#     def __init__(self, request_data):
#         raise NotImplementedError
