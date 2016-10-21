"""
Here is some temp code.
The idea behind hamster is to store event-to-task configuration
in a database, managed by a normal user.
This is actually mostly working, but the impl and inface keeps
changing and its a pita to manage.

So, for now, this configuration is going to be stored in a
static set of instances, requiring a code change to modify.

"""
import logging

from pipeline.gtfo import evaluate_criteria, safe_eval
from pipeline.pipeline import TaskSpec, schedule
from pipeline.state import LazyStateGetter, LazyTemplate
from pipeline.gtfo import Registry

logger = logging.getLogger(__name__)


class BaseTaskArgument(object):
    """Interface layer between our user interface (yaml) and the `pipeline` library.
    :attr name (str): the parameter name (python identifier)

    Subclasses are used to populate ``pipeline.TaskSpec``s
    """
    def __init__(self, name):
        """Task Arguments have a name, and optionally a task.
        If an arg has a task, callers should call with namespace,
        i.e. 'task.name'
        Stage is just for matching in pipeline.run()
        """
        self.name = name

    def make_arg(self):
        """Return a dict containing spec suitable for sending into pipeline.
        """


class TaskArgument(BaseTaskArgument):
    """A task argument that is just a name and value.
    :attr value (any): the argument
    """
    def __init__(self, name, value):
        super().__init__(name)
        self.value = value

    def make_arg(self):
        return {self.name: self.value}


class LazyTaskArgument(BaseTaskArgument):
    """A task argument that extracts a key out at runtime.
    :attr key (str): the name of the value extracted
    """
    def __init__(self, name, key):
        super().__init__(name)
        self.key = key

    def make_arg(self):
        return {self.name: LazyStateGetter(self.key)}


class TemplateTaskArgument(BaseTaskArgument):
    """A task argument that renders a jinja2 template at runtime.
    :attr template (str): the template
    """
    def __init__(self, name, template):
        super().__init__(name)
        if not isinstance(template, str):
            raise TypeError('template must be a string')
        self.template = template

    def make_arg(self):
        return {self.name: LazyTemplate(self.template)}


class Task(object):
    """Represents a build step - a celery task and it's arguments.

    :attr task_name (str): the task to run; must be in celery task registry
    :attr task_arguments (list): list of BaseTaskArgument instances
    """
    def __init__(self, task_name, task_arguments=None):
        self.task_name = task_name
        self.arguments = {}
        if task_arguments:
            for arg in task_arguments:
                self.arguments.update(arg.make_arg())


class Pipeline(object):
    """Store all the criteria for composing a pipeline.

    :attr tasks (list): list of Stages
    """
    def __init__(self, tasks):
        self.tasks = tasks

    def run(self, event_data):
        """Schedule the tasks with `pipeline`.

        :param event_data (dict): context data from the trigering event,
            if desired

        For each task in the pipeline, create a `pipeline.TaskSpec`
        storing the task information and the argument mapping. Send the
        list of specs in `pipeline.schedule`.

        This should be the only entry point into the `pipeine` module.
        """
        specs = []
        for task in self.tasks:
            spec = TaskSpec(
                task_name=task.task_name,
                kwargs=task.arguments
            )

            logger.debug('generated task spec {}'.format(spec))
            specs.append(spec)

        return schedule(specs, context=event_data)
