#!/usr/bin/env python

# Makes a test commit status on the most recent commit of a repo.
import os
from functools import partial
# requires github3.py==1.0.0a2
from github3 import GitHub, GitHubEnterprise



import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-u', dest='user', default=os.environ.get('HAMSTER_GITHUB_USER'))
parser.add_argument('-t', dest='token', default=os.environ.get('HAMSTER_GITHUB_API_TOKEN'))
parser.add_argument('-g', dest='github', default=os.environ.get('HAMSTER_GITHUB_HOST', 'github.com'))
parser.add_argument('-o', dest='owner', required=True)
parser.add_argument('-r', dest='repo', required=True)
parser.add_argument('--context', default='hamster')
parser.add_argument('--target-url', default='http://nowhere.com/1')
parser.add_argument('--description', default='test')
parser.add_argument('--state', default='success')

args = parser.parse_args()

assert args.state in ('pending', 'success', 'error', 'failure')
assert args.user
assert args.token

if args.github == 'github.com':
    gh = GitHub
else:
    gh = partial(
        GitHubEnterprise,
        args.github,
        verify=False
    )

github = gh(
    username=args.user,
    token=args.token
)

repository = github.repository(args.owner, args.repo)
sha = repository.commits().next().sha
repository.create_status(
    sha,
    args.state,
    target_url=args.target_url,
    description=args.description,
    context=args.context
)





