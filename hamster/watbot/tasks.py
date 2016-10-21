from pipeline.pipeline import state_aware_task

from hookshot.utils import refresh_session
from hookshot.tasks import pull_request_comment

from watbot.models import WatTracker

import logging
logger = logging.getLogger(__name__)


@state_aware_task
def emit_wat(pr):
    """Emit a comment to a pull request based on
    how many wats it already has.
    """
    import pdb; pdb.set_trace()
    refresh_session(pr)
    
    orgstr, repo = pr.repository

    # github.com has 'repos/orgname' as el 1 of 2-tuple,
    # but github ent has just 'orgname'
    # FIXME
    parts = orgstr.split('/')
    if len(parts) == 2:
        org = parts[1]
    else:
        org = parts[0]

    try:
        watcnt = WatTracker.objects.filter(
            org=org, repo=repo, number=pr.number
        ).get().watcnt
    except WatTracker.DoesNotExist:
        WatTracker.objects.create(
            org=org, repo=repo, number=pr.number
        )
        watcnt = 1

    template = "You have {} wats, @{}".format(watcnt, pr.user.login)
    pull_request_comment(pr, template)
