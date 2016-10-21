import pytest
from celery import chain
#from pipeline.tests.tasks import predicate_pass_through, state_tracking_pass_through
#from pipeline.tests.tasks import run_python_stub, output_xform_upper, print_stuff
from pipeline.pipeline import schedule, TaskSpec
from collections import OrderedDict

#pytestmark = pytest.mark.usefixtures('scoped_broker')

import logging
logger = logging.getLogger(__name__)

from github3.pulls import PullRequest

from functools import partial


class S(object):
    s = None


def test_multistage():
    source = S()
    source.s = 'somebody'
    config = [
        TaskSpec(
            'stage1', 'state_push', 'stage1', {'source': source, 'state': 'ginexi'}
        ),
        TaskSpec(
            'stage2', 'state_push', 'stage2', {'source': source, 'state': 'waters'}
        ),
    ]

    s = schedule(
        config,

    )
    ret = s.get()

    assert 1 == 1

