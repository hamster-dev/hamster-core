

import logging
logger = logging.getLogger(__name__)

class Source(object):
    @classmethod
    def make(cls, other):
        """Cast `other` to `cls`.
        """
        other.__class__ = cls
        return other

class OnDiskSource(Source):
    def acquisition_instructions(self):
        """Implementations must define how their on-disk
        representations can be acquired.
        """
        raise NotImplementedError
