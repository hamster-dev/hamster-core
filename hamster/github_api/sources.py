import os
import re

from django.conf import settings

from .utils import (
    get_pull_request_from_api_url, get_pull_request_from_url
)


class PullRequest(object):
    """Simple object that provides information about a pull request.
    """
    __id = 'pull_request'

    attrs = (
        'owner',
        'repository',
        'mergeable',
        'user',
        'number',
        'dest_branch',
        'ssh_url'
    )

    @classmethod
    def from_webhook(cls, hook_json):
        """Create a PullRequest object from `hook_json`.
        :param hook_json: Can be one of:
            - webhook json from a `pull_request` github api hook
            - webhook json from a `issue_comment` github api hook
        """
        if 'pull_request' in hook_json:
            return cls.from_json(hook_json['pull_request'])
        elif 'issue' in hook_json:
            pr_json = get_pull_request_from_api_url(
                hook_json['issue']['pull_request']['url']
            ).as_dict()
            return cls.from_json(pr_json)

        raise ValueError('unknown hook type')

    @classmethod
    def from_json(cls, data):
        """Deserialize a PullRequest from github api json (dict)."""
        return cls(
            owner=data['base']['repo']['owner']['login'],
            repository=data['base']['repo']['name'],
            mergeable=data['mergeable'],
            user=data['base']['user']['login'],
            number=data['number'],
            dest_branch=data['base']['ref'],
            ssh_url=data['base']['repo']['ssh_url']
        )

    def __init__(self, **kwargs):
        """This is temporary, and functional."""
        for k, v in kwargs.items():
            assert k in self.attrs
            setattr(self, k, v)

    @property
    def acquisition_instructions(self):
        return {
            # clone 'base' repo (pull destination)
            # fetch, then checkout the pull request
            # merge with the base branch
            'command': 'git clone {} {}'.format(self.ssh_url, self.repository),
            'directory': self.repository,
            'post_commands': [
                'git fetch origin refs/pull/{}/head'.format(self.number),
                'git checkout -b pr/{} FETCH_HEAD'.format(self.number),
                #FIXME merge conflicts will cause the following command to fail
                # the pipeline. If this is undesired, will need to figure out
                # how to make this conditional.
                'git merge origin/{}'.format(self.dest_branch)
            ]
        }
    def __str__(self):
        return "{}/{}#{}".format(self.owner, self.repository, self.number)


def get_dependent_prs(pr_obj):
    """Pull dependent pull requests from the body of a PR.
    :returns: list of ``github3.pullrequest`` objects.
    Note that this is not recursive.
    #TODO recurse and analyze the dependencies of the dependencies
    """
    pr_url_re = re.compile(r'({}/[\w]+/pull/[\d]+)'.format(
        os.path.join(settings.PIPELINE_GITHUB_URL, pr_obj.organization)
    ), re.M)
    matches = pr_url_re.findall(pr_obj.body)
    found = []
    for match in matches:
        pr = get_pull_request_from_url(match)
        if pr:
            found.append(pr)
    return found


class IssueComment(object):
    #TODO: refactor to resemble ``PullRequest``
    def __init__(self, hook_json):
        self._hook_json = hook_json

    @property
    def body(self):
        return self._hook_json["body"]