from django.db import models
from django.conf import settings
from jsonfield import JSONField

from pipeline.actions import TaskAction, ActionHook
from pipeline.criteria import evaluate_criteria
import pipeline.executor

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class EventSubscriberManager(models.Manager):
    """Manager responsible for EventSubscriber.
    """
    def matching_event(self, event):
        """Find subscribers for a given event.
        :param event: ``event.Event`` instance
        :returns: list of `EventSubscriber``s
        """
        results = []
        for subscriber in self.model.objects.filter(events__contains=event.name):
            if evaluate_criteria(event.data, subscriber.criteria):
                results.append(subscriber)

        return results


class EventSubscriber(models.Model):
    """Represents a subscriber to N events of a given type and composition.
    Attributes:
        events (list): List of subscribed event names.
            Example:
                ["pull_request.opened"]
        criteria (list): Criteria to be ANDed together to determine
            if a given event should be subscribed to. Each item should
            be a `pipeline.eval`` criteria (a three-tuple).
            Example:
                [
                    ["source.organization", "is", "octocat"],
                    ["source.repository", "is", "Hello-World"],
                ]
    """
    events = JSONField(default=[])
    criteria = JSONField(null=True)
    pipeline = models.ForeignKey('Pipeline')
    objects = EventSubscriberManager()

    class Meta:
        app_label = 'pipeline_django'


class Pipeline(models.Model):
    """Store all the criteria for composing a `pipeline.executor.Pipeline`.
    Attributes:
        name (str): Friendly name for the event handler.
            Example:
                "New PR checks"
        actions (list): Each item should be a dictionary that expresses
            a ``pipeline.actions.TaskAction``, and should be able to
            be serialized using ``self.from_dict()``.
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
            element should be used to run the pipeline.  Currently only
            'chain' is supported (indicates synchronous execution).
    TODO:
        - consider enaming this class to eliminate conflict
        with pipeline.executor.Pipeline
    """
    class Meta:
        app_label = 'pipeline_django'

    name = models.CharField(max_length=255)
    actions = JSONField()
    composition = models.CharField(
        max_length=32, choices=(('chain', 'chain'), ('group', 'group')), default='chain'
    )


    def deserialize(self):
        """Deserialize `actions` into objects appropriate for building a pipeline.
        :returns: list of ``TaskAction``s
        """
        return [self.action_from_dict(dct) for dct in self.actions]

    @staticmethod
    def action_from_dict(dct):
        """Build a ``pipeline.action.TaskAction`` from dictionary.
        :param dct: a dict containing the data required to build a TaskAction
        :returns: ``pipeline.actions.TaskAction``
        """
        hooks = []
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

    def schedule(self, event_data):
        """Send to `pipeline.executor` to be scheduled.
        :param event_data (dict): An Event's `data` property.
        :returns: AsyncResult
        """
        data = event_data.copy()
        task_actions = self.deserialize()
        pl = pipeline.executor.Pipeline(
            data.pop('source'), task_actions,
            composition=self.composition
        )
        pl.context.update(data)
        pl.context.update({'secrets': settings.SECRETS})
        for module_path in settings.HAMSTER_FILTER_MODULES:
            pl.context.register_filters(module_path)

        return pl.schedule()
