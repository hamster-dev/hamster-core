from __future__ import print_function
import os.path

from fabric.api import task, run, cd
from fabric.contrib.files import exists


@task
def list():
    """List running containers on the system."""
    run('docker ps')

@task
def install(pth, repo, branch=None):
    """Make a clean install of the application.
    Danger: will remove any existing containers, including the database.
    """
    if exists(pth):
        print("Cannot install to {}; app exists.".format(pth))
        return

    destdir = os.path.basename(
        pth.rstrip(os.path.sep)
    )
    destcwd = os.path.dirname(
        pth.rstrip(os.path.sep)
    )

    with cd(destcwd):
        run('git clone {} {}'.format(repo, destdir))
        with cd(destdir):
            if branch:
                run('git checkout {}'.format(branch))
            run('make scratch')

@task
def deploy(pth, branch=None):
    """Deploy updates to the application."""
    with cd(pth):
        run('git checkout -- .')   # clean up any crap I forgot
        run('git pull origin {}'.format(branch or 'master'))
        run('make update')