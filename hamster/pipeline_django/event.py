"""
Simple event registration system.

This is inelegant, but will work for now.
In particular, the Event class needs to be redesigned.

TODO:
    - I owuld like to remove the `source` proprty, since it is
    included in `data`.  I am not sure if it is required anywhere else.

"""
from cached_property import cached_property

from pipeline.bases import Registry
from pipeline.eval import evaluate_criteria

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)



class Event(metaclass=Registry):
    """Base event class.
    Event lookup is expensive, this should be refactored.  Good enough for now.
    """
    criteria = None

    def __init__(self, input_data):
        """Events should *only* require input_data to be deserialized.
        Filtering which events to fire should be done at the classmethod level.
        """
        self._input_data = input_data

    @classmethod
    def find_matching(cls, input_data):
        """Find events that match a given input.

        Matches the events criteria against the event-specific
        deserialized input data.

        Multiple events may match a single input.
        """
        available = cls.getlist()
        found = []
        for klass in available:
            instance = klass(input_data)
            if instance._is_relevant(): found.append(instance)
        return found

    @cached_property
    def data(self):
        """Return deserialized event data.
        """
        return {
            'source': self.source,
            'event': self.name
        }

    @cached_property
    def source(self):
        """Return the deserialized source."""
        raise NotImplementedError

    def _is_relevant(self):
        """Check to see if the event matches input, by
        matching self.criteria to self.data

        :returns: bool
        """
        return evaluate_criteria(self.data, self.criteria)

    @cached_property
    def name(self):
        """Provide a friendly name for consumers to indicate their
        interest in an event.
        TODO: this uses a workaround for private class variables
        (prepended with dunderscore).  See if there is a way that
        I can continue to use this technique (it is required for
        other parts of the system) but not have to resort to these
        getattrs to read them.
        """
        return getattr(self, '_{}__id'.format(self.__class__.__name__))
