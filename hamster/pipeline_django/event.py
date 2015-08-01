"""
Simple event registration system.

"""
from cached_property import cached_property

from pipeline.bases import Registry
from pipeline.actions import TaskAction
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
    def handle_events(cls, event_klass, *args, **kwargs):
        """Route events to the stored event handler."""
        events = event_klass.find_relevant(
            *args, **kwargs
        )
        if not len(events):
            return []

        logger.debug("found events {}".format(events))
        async_results = []
        for event in events:

            event_handlers = cls.search(
                event
            )
            logger.debug("found event handlers {}".format(event_handlers))

            for handler in event_handlers:
                if not handler.enabled:
                    continue

                source = event.data['source']
                task_actions = [cls.action_from_dict(dct) for dct in handler.actions]
                pl = Pipeline(task_actions, composition=handler.composition)

                async_results.append(pl.schedule(
                    source,
                    **event.data
                ))

            async_results.extend(event.fire(event_handlers))

        return async_results

    @staticmethod
    def action_from_dict(dct):
        """Build task action from dictionary.
        """
        hooks = []  # list of tuples
        if 'hooks' in dct:
            for item in dct['hooks']:
                # because predicate is not a normal task attribute, pop it before serializing
                # default of 'True' will cuase it to always execute.
                predicate = item.pop('predicate', 'True')
                hooks.append((
                    PipelineEventHandler.action_from_dict(item),
                    predicate
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