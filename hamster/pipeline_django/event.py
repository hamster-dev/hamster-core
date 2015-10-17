"""
Simple event registration system.

This is inelegant, but will work for now.
In particular, the Event class needs to be redesigned.

TODO:
    - I owuld like to remove the `source` proprty, since it is
    included in `data`.  I am not sure if it is required anywhere else.

"""
from cached_property import cached_property

from pipeline.registry import Registry

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Event(metaclass=Registry):
    """Base event class.
    """

    def __init__(self, event_input):
        self._event_input = event_input

    @classmethod
    def matches_input(cls, event_input):
        """Determine if a given Event subclass matches the provided input.
        :param event_input: some input
        :returns: bool
        """
        return True

    @classmethod
    def find_matching(cls, event_input):
        """Find event subclasses that match a given input.

        Will only find subclasses of `cls`, not all registered events.
        Returns a list of Events instantiated with the supplied input.

        :param event_input: some input
        :returns: sorted list of Event instances
        """
        registered = cls.getlist()
        return sorted([
            klass(event_input) for klass in registered if klass.matches_input(event_input)
        ])

    @cached_property
    def data(self):
        """Expose some data to the system.
        """
        return {}

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

    def __lt__(self, other):
        """In order to order events, we need them to be orderable.
        Just order them by event name for now.
        """
        return self.name < other.name

    # def __repr__(self):
    #     return "{}/{}/{}".format(self.__class__.__name__, self.name, self.data.keys())