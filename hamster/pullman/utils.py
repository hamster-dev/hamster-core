"""
Observations about github3:
    It does not appear to be possible, or at least robust, to
    use webhook json data to create instances of github api objects
    exposes by github3.
    I have to grab the data that I need in order to use the github3 api
    to properly access the objects.  This is wasteful, and annoying.
"""
from functools import partial
from django.conf import settings
from github3 import GitHub, GitHubEnterprise, GitHubError
from github3.null import NullObject

import logging
logger = logging.getLogger(__name__)


def issue_is_pullrequest(issue):
    """Determine if an issue is a pull request.
    """
    return bool(issue.pull_request())


def get_pull_at_head(organization, repository, sha):
    """Find a pull request having HEAD at given sha.
    """
    gh = github()
    repo = gh.repository(organization, repository)
    possible_pulls = repo.issues(
        state='open',
        sort='updated',
        direction='desc'
    )
    for candidate in possible_pulls:
        if issue_is_pullrequest(candidate):
            pull = candidate.pull_request()
            if pull.head.sha == sha:
                return pull


def get_commit_status(organization, repository, sha, id):
    """It is really a pain in the motherfucking ass.
    Wy the fuck can't is have a "CommitStatus.from_json(hook_json)"?h
    """
    # read every.fucking.status from the repository,
    # and filter the results based on (sha, id)
    gh = github()
    repo = gh.repository(organization, repository)
    statuses = list(filter(lambda s: s.id==id, repo.statuses(sha)))
    assert len(statuses) == 1, 'got >1 commit status for sha {}'.format(sha)
    return statuses[0]


def get_pip_uri_from_pullrequest(pr_obj):
    """Derive a pip uri from a pull request."""
    return "git+{}@{}".format(pr_obj.head.clone_url, pr_obj.head.sha)


def check_null(obj):
    """The github3.py library will return a NullObject if there was
    an issue with an api call.  I am not exactly sure why or
    exactly when this happens, so this stub function exists until it
    can be investigated.
    """
    if isinstance(obj, NullObject):
        raise RuntimeError('github api returned a null object')
    return obj


def get_pull_request_from_api_url(url):
    """Get a github3.pulls.PullRequest object from an URL.
    #TODO: figure out why we need the exception handelr here.
    Why is there >1 url format?
    """
    try:
        from urllib.parse import urlparse
    except ImportError:
        import urlparse

    # this *should* work as long as you dont pass any crap in
    try:
        _, _, _, _, org, _repo, _, number = urlparse(url).path.split('/')
    except ValueError:
        # this only hapens in my tests, when I use the sample data
        # provided by github in their api docs
        _, _, org, _repo, _, number = urlparse(url).path.split('/')
    gh = github()
    return check_null(gh.pull_request(org, _repo, number))


def get_pull_request_from_url(url):
    """Get a github3.pulls.PullRequest object from an URL.
    """
    try:
        from urllib.parse import urlparse
    except ImportError:
        import urlparse

    # this *should* work as long as you dont pass any crap in
    _, org, repo, _, number = urlparse(url).path.split('/')

    gh = github()
    repo = gh.repository(org, repo)
    return check_null(repo.pull_request(number))


def install_pr_webhook(org, repo, endpoint):
    """Set up a Github pull request webhook."""
    hook_config = {
        'url': endpoint,
        'content-type': 'json'
    }
    gh = github()

    repo = gh.repository(org, repo)

    hook = repo.create_hook(
        'web', hook_config, ['pull_request'], active=True
    )

    if not hook:
        logger.error("Could not install hook")
        return False

    return True


def list_hooks(org, repo):
    """List the hooks in a repo"""
    gh = github()
    repo = gh.repository(org, repo)

    for hook in repo.iter_hooks():
        yield hook


def github():
    """Get a connection to some github.
    Queries settings to see if that should be github enterprise, or github.com.

    This chould probably changed to a class

    Note: the ``requests`` library, which github3.py is based upon, will
    read ~/.netrc ~/_netrc files for stored github authentication.
    It **WILL** override provided auth **IF** it is an auth failure.
        - @mikewaters, who spent many hours pulling out hair to see why
            logins were successful when they shouldnt be.
    There is an attr ``requests.sessions.SessionRedirectMixin.trust_env``
    that can be modified to chaneg this behavior, but github3.py does not support
    this attr. #TODO open a PR to github3.py?
    The shitty side-effect of this is this function will NOT raise an exception,
    and it will provide a Github instance to the caller, which will yield
    gitub3.NullObjects when api calls are made that *SHOULD* instead fail with an
    authorization error.
    """
    if not hasattr(settings, 'HAMSTER_GITHUB_URL') \
            or not settings.HAMSTER_GITHUB_URL\
            or settings.HAMSTER_GITHUB_URL.endswith('github.com'):
        TheHub = GitHub
    else:
        TheHub = partial(
            GitHubEnterprise,
            settings.HAMSTER_GITHUB_URL,
            verify=False  # not sure if we need to verify SSL anymore
        )
    try:
        gh = TheHub(
            username=settings.HAMSTER_GITHUB_USERNAME,
            token=settings.HAMSTER_GITHUB_TOKEN
        )
        gh.me()  # force a connect attempt, which will raise 401 if login failure
    except GitHubError as ex:
        logger.error("error connecting to github: {}".format(str(ex)))
        raise
    else:
        return gh
