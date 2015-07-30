from django.db import models

from jsonfield import JSONField

from pipeline.actions import TaskAction
from pipeline.eval import evaluate_criteria
from pipeline.executor import Executor

from pipeline_django.event import EventHandler

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

#TODO: move some functionality to a Manager

class PipelineEventHandler(models.Model):
    """Model for storage of ``pipeline.event.EventHandler``s in a database.

    Implements the same interface as ``pipeline.event.EventHandler``.

    Attributes:
        name (str): Friendly name for the event handler.
            Example:
                "New PR checks"
        events (list): List of event names to handle.
            Example:
                ["pull_request.opened"]
        criteria (list): Criteria to be ANDed together to determine
            if a given event should  be handled. Each item should
            be a `pipeline.eval`` criteria (a three-tuple).
            Example:
                [
                    ["source.organization", "is", "octocat"],
                    ["source.repository", "is", "Hello-World"],
                ]

        actions (list): Each item should be a dictionary that expresses
            a ``pipeline.actions.TaskAction``, and should be able to
            be serialized using ``pipeline.actions.TaskAction.from_dict()``.
            Example:
                [
                    {
                        "name": "mergeability_check",
                        "action": "pull_request_mergeable",
                        "workspace": "python3",
                        "workspace_kwargs": {
                            "delete": False
                        },
                        "callbacks": [
                            {
                                # this is a failure handler
                                "predicate": "not mergeability_check",
                                "action": "pull_request_comment",
                                "kwargs": {
                                    "message": "@{{ source.user }}: merge conflicts"
                                }
                            }
                        ]
                    }
                ]
        enabled (bool): Whether or not this event handler should be
            considered for any events.
        app_name (str): The app a given event handler is associated with.
            Empty string indicates that it is associated with all apps.

    """
    class Meta:
        app_label = 'pipeline_django'

    name = models.CharField(max_length=255)
    events = JSONField(default=[])
    criteria = JSONField(null=True)
    actions = JSONField()
    enabled = models.BooleanField(default=True, null=False)
    app_name = models.CharField(max_length=64, blank=True)


    @classmethod
    def search(cls, event, app_name=''):
        """Find any configurations that match event, source.
        This is terribly inefficient, but for now it is functional.
        TODO: move to a manager
        """
        results = []

        for stored_handler in cls.objects.filter(app_name=app_name):
            if not event.name in stored_handler.events:
                continue

            if evaluate_criteria(event.data, stored_handler.criteria):
                results.append(stored_handler)

        return results

    def __str__(self):
        return "{}/{}/{}".format(self.name, self.events, self.criteria)

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
                executor = Executor()

                async_results.append(executor.schedule(
                    [TaskAction.from_dict(dct) for dct in handler.actions],
                    source,
                    **event.data
                ))

            async_results.extend(event.fire(event_handlers))

        return async_results
