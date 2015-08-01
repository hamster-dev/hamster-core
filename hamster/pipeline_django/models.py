from django.db import models
from jsonfield import JSONField

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
    composition = models.CharField(max_length=32, default='chain')
    enabled = models.BooleanField(default=True, null=False)
    app_name = models.CharField(max_length=64, blank=True)

    def __str__(self):
        return "{}/{}/{}".format(self.name, self.events, self.criteria)