"""
Simple event registration system.

"""
from cached_property import cached_property

from pipeline.executor import Executor
from pipeline.actions import TaskAction
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
    def find_relevant(cls, input_data):
        """Find events relevant to a given input.
        Multiple events may match a single input.
        Matches the events criteria against the event-specific
        deserialized input data.
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

    def fire(self, handlers):
        """Send event to a list of handlers."""
        assert isinstance(handlers, (list, tuple))

        async_results = []
        for handler in handlers:
            async_results.append(handler.handle_event(self))

        return async_results


class EventHandler(object):
    """Class to act on an event.
    uses celery as the executor
    Makes little sense to deinfe these in code, typically
    these wuld be serialized from outside the source code.
    """
    def __init__(self, name, events=None, criteria=None, actions=None, enabled=True):
        """
        Params:
            name (str)
            events (list of str)
            criteria (list of str)
            actions (list of dict)
            enabled (bool)

        Default behavior:
            - events: handle no events
            - criteria: match all criteria
            - actions: do nothing
        """
        self.name = name
        self.events = events or []
        self.criteria = criteria
        self.actions = actions or []
        self.enabled = enabled

    @property
    def pipeline(self):
        """Return the build pipeline, which is just a list of the
        (celery) TaskActions associated with the event handler.
        """
        return [TaskAction.from_dict(dct) for dct in self.actions]

    def handle_event(self, event):
        """Execute the actions contained in the event handler
        using an executor, uisng the event data.
        """
        #z()
        if not self.enabled:
            #TODO should we communicate to caller using exception?
            return None

        try:
            source = event.data.pop('source')
        except KeyError:
            logger.error('Source is required in event data {}:{}'.format(self, event))
            raise

        executor = Executor()
        return executor.schedule(
            self.pipeline,
            source,
            **event.data
        )