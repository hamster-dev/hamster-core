from celery import shared_task
import subprocess
from .workspace import Workspace


import logging
logger = logging.getLogger(__name__)

from io import StringIO
import sys

class Capturing(list):
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self
    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        sys.stdout = self._stdout


class CommandSessionResult(object):
    """Class for encapsulating results of a shell
    command session.
    """
    def __init__(self, session):
        #TODO add more stuff here
        self.output = session.last_output
        self.returncode = session.last_returncode
        self.log = session.log

from .pipeline import state_aware_task
#@shared_task(name='shell_command')
@state_aware_task(name='shell_command')
def shell_command(source, commands):
    """Run a sequence of shell commands.
    If any command returns nonzero, stop execution.
    """
    from hookshot.utils import refresh_session
    refresh_session(source)
    print('qqqqqqqqqqqqqqqqq')
    #import ipdb; ipdb.set_trace()
    #pytest.set_trace()
    assert isinstance(commands, (list, tuple))

    with Workspace(source) as workspace:
        for command in commands:
            logger.debug('Running command {}'.format(command))
            try:
                workspace.session.check_call(command)
            except subprocess.CalledProcessError as ex:
                logger.debug('Command {} failed with {}.'.format(
                    command, str(ex)
                ))
                break
            else:
                logger.debug("Command {} succeeded.".format(
                    command
                ))
            finally:
                logger.debug("Comand {} returned code {}".format(
                    command, workspace.session.last_returncode)
                )
        return CommandSessionResult(workspace.session)

@state_aware_task(name='state_push')
def state_push(source, state):
    """Just returns provided `state`, to push into state tracker."""
    return state

#@state_aware_task(name='get_maintainers')
#def get_maintainers(source):
#    return ['mike', 'babs']

class X(object):
    y = None

#@state_aware_task(name='pull_request_assign')
#def pull_request_assign(source, whom):
#    # tasks that have an erorr condition MUST raise an exception
#    print('assigning pr {} to {}'.format(source, whom))
#    x = X()
#    x.y = 'xy'
#    return x
#
#@state_aware_task(name='pull_request_comment')
#def pull_request_comment(source, message):
#    print('commenting on pr {} with {}'.format(source, message))
#    return True
