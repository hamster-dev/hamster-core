from django.db import models
from jsonfield import JSONField

from pipeline.actions import TaskAction, ActionHook
from pipeline.eval import evaluate_criteria
from pipeline.pipeline import Pipeline

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

#TODO: break this up into two models,

class PipelineEventHandlerManager(models.Manager):

    def find_for_event(self, event, app_name=''):
        """Find any handlers that subscribe to an event.

        :param event: instance of ``pipeline_django.event.Event``
        :param app_name: optionally filter results by ``app_name`` property
        :returns: list of ``models.PipelineEventHandler``s

        TODO: do we still need app_name?
        """
        results = []

        for stored_handler in self.model.objects.filter(app_name=app_name):
            if not event.name in stored_handler.events:
                continue

            if evaluate_criteria(event.data, stored_handler.criteria):
                results.append(stored_handler)

        return results

    def handle_events(self, events):
        """Route events to the stored event handlers.

        :param events: list of ``pipeline_django.event.Event`` instances
        :returns: list of ``celery.result.AsyncResult``s
        """

        async_results = []

        for event in events:
            event_handlers = self.find_for_event(event)

            if not event_handlers:
                logger.debug("no event handlers for".format(event))
                continue

            logger.debug(
                "found event handlers {} for event {}".format(event_handlers, event)
            )

            for handler in event_handlers:
                ret = self.handle_single_event(event, handler)
                if ret:
                    async_results.append(ret)

        return async_results

    @staticmethod
    def handle_single_event(event, handler):
        """Fire a single event handler.

        :param event: instance of ``pipeline_django.event.Event``
        :param handler: instance of ``models.PipelineEventHandler``
        :returns: async result if success, None otherwise
        """
        if not handler.enabled:
            return

        data = event.data.copy()
        source = data.pop('source')
        task_actions = handler.deserialize()
        pl = Pipeline(task_actions, composition=handler.composition)

        return pl.schedule(
            source,
            **data
        )


class PipelineEventHandler(models.Model):
    """Model for storage of Event Handlers in a database.

    An Event Handler defines what events is subscribes to, as well
    as the actions that should be performed when a relevant event occurs.
    These actions are executed in a ``pipeline.Pipeline``, so this
    model also includes details on how that pipeline should be created.

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
            Sparse example:
                [
                    {
                        "name": "do_something",
                        "action": "do_the_thing_task"
                    }
                ]
            Full example:
                [
                    {
                        "name": "mergeability_check",
                        "action": "pull_request_mergeable",
                        "workspace": "python3",
                        "workspace_kwargs": {
                            "delete": False
                        },
                        "hooks": [
                            {
                                "predicate": "not mergeability_check",
                                "event": "post",
                                "action": "pull_request_comment",
                                "kwargs": {
                                    "message": "@{{ source.user }}: merge conflicts"
                                }
                            }
                        ]
                    }
                ]
        composition (str): pipeline composition - which celery canvas
            element shoyld be used to run the pipeline.  Currently only
            'chain' is supported (indicates synchronous execution).
        enabled (bool): Whether or not this event handler should be
            considered for any events.
        app_name (str): The app a given event handler is associated with.
            Empty string indicates that it is associated with all apps.

        TODO:
            - separate the `actions` out into another model, so they can
            be reused.  also use a more easily understandable abstraction,
            not just a bunch of json.
    """
    class Meta:
        app_label = 'pipeline_django'

    name = models.CharField(max_length=255)
    events = JSONField(default=[])
    criteria = JSONField(null=True)
    actions = JSONField()
    composition = models.CharField(max_length=32, default='chain')
    enabled = models.BooleanField(default=True, null=False)
    app_name = models.CharField(max_length=64, blank=True)

    objects = PipelineEventHandlerManager()

    def __str__(self):
        return "{}/{}/{}".format(self.name, self.events, self.criteria)

    def deserialize(self):
        """Return a list of fully-formed ``pipeline.action.taskActions``s
        that will be used to populate the build pipeline.
        """
        return [PipelineEventHandler.action_from_dict(dct) for dct in self.actions]

    @staticmethod
    def action_from_dict(dct):
        """Build a ``pipeline.action.TaskAction`` from dictionary.
        """
        hooks = []

        # this block is for compat with pipeline==0.10 #FIXME
        if 'callbacks' in dct:
            stored_hooks = dct['callbacks']
        else:
            stored_hooks = dct.get('hooks', [])

        # Each hook should have the same keys as an action,
        # except for the additional 'event' and 'predicate' keys,
        # and it should not have it's own hooks.
        for hook in stored_hooks:
            hooks.append(ActionHook(
                hook['action'],
                predicate=hook.get('predicate', None),
                event=hook.get('event', None),
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
