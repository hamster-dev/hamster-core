from django.db import models
from django.core.exceptions import ValidationError

from yamlfield.fields import YAMLField

from pipeline.gtfo import evaluate_single_criterion, safe_eval

from core.pipeline import (
        Task, Pipeline, 
        TaskArgument, LazyTaskArgument, 
        TemplateTaskArgument,
    )
from core.bot import Bot

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def validate_yaml(value):
    """Check a few things before save, so search doesnt blow up.
    """
    #FIXME: modify this for nested lists, if req'd
    #for criteria in value['subscriber']['criteria']:
    #    expr = criteria.split(' ')
    #    if not len(expr) == 3 or expr[1] != 'is':
    #        raise ValidationError("Only 'is' operator supported or bad expression")


class EventSubscriberManager(models.Manager):
    """Manager responsible for EventSubscriber.
    """
    def matching_event(self, event):
        """Find subscribers for a given event.
        :param event: ``event.Event`` instance
        :returns: list of `EventSubscriber``s
        """
        results = []

        for subscriber in self.model.objects.all():
            if event.name in subscriber.events:
                for item in subscriber.criteria:
                    if evaluate_single_criterion(event.data, item):
                        logger.debug('Found matching subscriber {}'.format(subscriber))
                        results.append(subscriber)

        return results


class EventSubscriber(models.Model):
    """Represents a subscriber to an event of a given type and composition,
    and the Pipeline that will be scheduled if a matching event is fired.

    :attr events (list): List of subscribed event names.
        Example:
            ["pull_request.opened"]
    :attr pipeline (Pipeline): the pipeline to be executed
    """
    data = YAMLField(validators=[validate_yaml])
    objects = EventSubscriberManager()

    class Meta:
        app_label = 'core'

    def _get_prop(self, which):
        """Grab subscriber property from derialized YAML.
        """
        ret = []

        try:
            sub = self.data['subscriber']
            ret.extend(sub[which])
        except Exception as exc:
            # we eat exceptions here because the properties are used for filtering
            logger.error(exc)
        
        return ret

    @property
    def events(self):
        return self._get_prop('events')

    @property
    def criteria(self):
        """Return subscriber criteria.
        """
        return self._get_prop('criteria')

    @property
    def pipeline(self):
        """Stuff some of deserialized YAML into a `core.pipeline.Pipeline`.
        """
        if 'pipeline' in self.data:
            tasks = []
            for _task in self.data['pipeline']:
                if isinstance(_task, str):
                    # this is a task that accepts no parameters,
                    # or user wants to use defaults.
                    tasks.append(Task(_task))
                    continue

                # task has paramaters and user want to set them
                for task_name, args in _task.items():
                    task_args = []
                    for arg_name, arg_value in args.items(): 
                        # we should use ansible yaml parser to do this properly
                        # so, this is a hack
                        if isinstance(arg_value, str):
                            try:
                                # Lazy or TemplateTaskArgument
                                arg_type, value = arg_value.split('=')
                                if arg_type == 'lazy':
                                    task_args.append(LazyTaskArgument(arg_name, value))
                                elif arg_type == 'template':
                                    task_args.append(TemplateTaskArgument(arg_name, value))
                                else:
                                    raise ValueError
                            except ValueError:
                                # normal TaskArgument having string
                                task_args.append(TaskArgument(arg_name, arg_value))
                        else:
                            # normal TaskArgument having non-string
                            task_args.append(TaskArgument(arg_name, arg_value))

                    tasks.append(Task(task_name, task_args))

            return Pipeline(tasks)

        elif 'bot' in self.data:
            bot = Bot.get(self.data['bot']['name'])()
            return Pipeline(bot.tasks)
        else:
            raise ValueError
