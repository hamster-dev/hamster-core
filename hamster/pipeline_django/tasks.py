from pipeline import action

import logging
logger = logging.getLogger(__name__)

@action
def emit_log(self, source, message):
    logger.debug("{} for {}".format(message, source))