"""
Simple event registration system.

"""
from cached_property import cached_property

from pipeline.bases import Registry
from pipeline.actions import TaskAction, ActionHook
from pipeline.eval import evaluate_criteria
from pipeline.pipeline import Pipeline

from pipeline_django.models import PipelineEventHandler

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



class EventHandler(object):

    @classmethod
    def search(cls, event, app_name=''):
        """Find any configurations that match event, source.
        This is terribly inefficient, but for now it is functional.
        TODO: move to a manager
        """
        results = []

        for stored_handler in PipelineEventHandler.objects.filter(app_name=app_name):
            if not event.name in stored_handler.events:
                continue

            if evaluate_criteria(event.data, stored_handler.criteria):
                results.append(stored_handler)

        return results

    @classmethod
    def handle_event(cls, event, handler):
        """Fire a single event handler.
        :returns: async result if success, None otherwise
        """
        if not handler.enabled:
            return

        data = event.data.copy()
        source = data.pop('source')
        task_actions = [cls.action_from_dict(dct) for dct in handler.actions]
        pl = Pipeline(task_actions, composition=handler.composition)

        return pl.schedule(
            source,
            **data
        )

    @classmethod
    def handle_events(cls, events):
        """Route events to the stored event handler."""

        async_results = []

        for event in events:

            event_handlers = cls.search(
                event
            )
            if not event_handlers:
                logger.debug("no event handlers for".format(event))
                continue

            logger.debug(
                "found event handlers {} for event {}".format(event_handlers, event)
            )

            for handler in event_handlers:
                ret = cls.handle_event(event, handler)
                if ret:
                    async_results.append(ret)

        return async_results

    @staticmethod
    def action_from_dict(dct):
        """Build task action from dictionary.
        """
        hooks = []

        # Each hook should have the same keys as an action,
        # except for the additional 'event' and 'predicate' keys,
        # and it should not have it's own hooks
        for hook in dct.get('hooks', []):
            # because predicate is not a normal task attribute, pop it before serializing
            # default of 'True' will cuase it to always execute.
            predicate = hook.pop('predicate', None)
            event = hook.pop('event', None)
            hooks.append(ActionHook(
                hook['action'],
                predicate=predicate,
                event=event,
                **hook.get('kwargs', {})
            ))

        workspace_cls = dct.get('workspace')
        workspace_kwargs = dct.get('workspace_kwargs')

        task_action = TaskAction(
            dct['action'],
            name=dct.get('name'),
            hooks=hooks,
            workspace=workspace_cls,
            workspace_kwargs=workspace_kwargs,
            **dct.get('kwargs', {})
        )

        return task_action