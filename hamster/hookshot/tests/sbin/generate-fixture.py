"""
Generate json for some github object.

Usage: $0 org repo number > fixture-file.json
Currently only 'pull request' object is supported

Why:
    Github3.py objects can be instantiated from json, but in order
    to get that json you need to instantiate one from the network first.

How:
    Use the hookshot api to connect to the project-defined github,
    make the github api call, and serialize the response to json.
"""
import os
import sys

from github3.pulls import PullRequest

pth = os.path.dirname(os.path.dirname(os.getcwd()))
sys.path.insert(0, pth)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hookshot.tests.settings")

from hookshot.utils import github


def main(org, repo, number):
    """retrieve a pul request and dump it to stdout.
    """
    gh = github()
    pr = gh.pull_request(org, repo, number)
    print(pr.as_json())


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('org')
    ap.add_argument('repo')
    ap.add_argument('number')

    args = ap.parse_args()

    main(
        args.org,
        args.repo,
        args.number
    )
