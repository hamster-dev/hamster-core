"""
Pipeline rearch

"""
import types
import collections
import importlib
import six
import inspect
from celery import Task, shared_task, current_app
from celery import chain
from celery.exceptions import Ignore, Reject
from collections import OrderedDict
import functools

from .state import StateTracker, LazyStateGetter, Template, LazyTemplate

import logging
logger = logging.getLogger(__name__)

class TaskSpec(object):
    """Specification for a task.
    A task has a single return value, and that value is pushed into the
    StaeTracker using the key `result_name`, where it is accessible from
    other tasks.
    """
    def __init__(self, task_name, result_name=None, kwargs=None):
        self.task_name = task_name  # names a task in the registry
        self.result_name = result_name if result_name else task_name  # has to be a valid python identifier

        # kwargs should be a dict of base types, StateGetters, StateEvaluators
        self.kwargs = kwargs or {}


def schedule(task_spec, composition='chain', context=None):
    """Schedule tasks to be executed on a worker.
    :param task_spec (list): list of `TaskSpec` instances
    :param composition (str): which celery canvas element to use (only chain supported)
    :param context (dict): additional data to be applied to the task list
    :returns: AsyncResult
    """
    result_names = [n.result_name for n in task_spec]
    # result_names have to be unique
    assert len(result_names) == len(set(result_names))

    assert composition == 'chain', 'only chain() supported'

    if context:
        assert isinstance(context, dict)

    tasks = []

    for spec in task_spec:
        task = current_app.tasks[spec.task_name]
        params = spec.kwargs.copy()

        # get the task's arguments so that we can fill them in from context
        task_args = inspect.signature(task).parameters.keys()

        #if context:
        #    for k, v in context.items():
        #        # only populate args from context if they aren't already
        #        # present (user should be able to override)
        #        #TODO: why do we need this?  User can populate TaskSpec
        #        # with whatever startup values they like.
        #        if k in task_args and not k in params:
        #            params[k] = v

        # inject an identifier into the signature so we know how to
        # name it's key in the state tracker
        params['_pipeline_result_variable_name'] = spec.result_name

        # put StageGetters into params for those arguments that
        # should be evaluated at task runtime, using data from
        # previous tasks in the chain
        #for inject_k, inject_v in spec.inject_kwargs.items():
        #    params[inject_k] = StateGetter(inject_v)

        initial_chain_state = StateTracker()
        if context:
            # add passed-in context as 'event'
            #TODO: this should be in caller's api, not ours
            event_data = StateTracker()
            event_data.update(context)  # this is a stupid way to do this
            initial_chain_state.update({'event': event_data})
        if len(tasks) == 0:
            # we need to prime the initial chain state, because some
            # tasks args, like templates, may need the initial cintext
            # data to be in the chain state (the resultss of previous tasks
            # may not be sufficient)
            tasks.append(task.s(initial_chain_state, **params))
        else:
            tasks.append(task.s(**params))

    #import ipdb; ipdb.set_trace()
    #tasks = [tasks[0]]
    return chain(*tasks).delay()


def pipeline_task_wrapper(f):
    """This decorator is responsible for wrapping execution of the actual 
    celery task; it will be called on the worker, and will receive
    the StateTracker from the calling task (or nothing if this is the first task
    in a chain).
    Notes:
        we only allow keyword args, because we steal the first non-keyarg
        for the chain state.  perhaps this can instead be done with an intance
        variable, to allow us to pass args as well as keyargs?
    """
    @functools.wraps(f)
    def newf(*args, **kwargs):
        task_name = kwargs.pop('_pipeline_result_variable_name')

        # when executed in a chain, the first arg
        # to a non-first task wil be the return value
        # of the previous task.
        # because we are fucking with the chain, we dont
        # care about these at all, currently
        if len(args) > 1:
            # we can assume that the first non-self arg is the result of the
            # previous link in the chain
            #TODO(mikew): this logic will fail if we allow non-keyword args
            chain_state = args[1]
        elif len(args) == 1:
            chain_state = args[0]
        else:
            assert False, 'should not happen'
            chain_state = StateTracker()

        # extract any data from state tracker that the function requires
        for k, v in kwargs.items():
            if isinstance(v, LazyStateGetter):
                kwargs[k] = v.extract(chain_state)
            elif isinstance(v, LazyTemplate):
                kwargs[k] = v.render(chain_state)
        # run kwargs through templating engine;
        # at this point all of kwargs contain actual data
        #for k, v in kwargs.items():
        #    #import ipdb; ipdb.set_trace()
        #    if isinstance(v, six.string_types):
        #        kwargs[k] = chain_state.render_template(v, **kwargs)

        #TODO(mikew): only kwargs are supported by this system currently
        ret = f(**kwargs)

        setattr(chain_state, task_name, ret)

        return chain_state

    # There are some incompatibilities between celery and functools.wraps
    # with respect to sending wrapped functions as tasks.
    # Because celery relies on __module__.__name__ for task identification, and since
    # we don't want all tasks to have the same name 'pipeline.actions.newf', we must
    # manually modify __name__ and __module__.
    newf.__name__ = f.__name__
    newf.__module__ = f.__module__
    return newf


def state_aware_task(*args, **kwargs):
    """Decorator for tasks that wish to utilize state tracking.
    This is a replacement for (and a wrapper of) the `shared_task` decorator.
    
    TODO (mikew): It would be preferable to figure out a way to allow the 
        standard celery decorators to be used, as that would allow us to
        wrap any pre-existing celery task in a state tracker.
    """
    def wrapper(**_kwargs):
        def __inner(func):
            if not 'name' in _kwargs:
                _kwargs['name'] = func.__name__
            return shared_task(pipeline_task_wrapper(func), **_kwargs)
        return __inner

    # tasks must be bound for any of this to work,
    # or else we won't have access to the Task instance
    # upon which we hang t he StateTracker
    kwargs['bind'] = True

    # below code would be used is we had subclass of `Task`,
    # keep it around until we are sure we don't need it. @mikew
    #kwargs['base'] = StateTrackingTask
    
    # this code is stolen right out of celery
    if len(args) == 1 and callable(args[0]):
        return wrapper(**kwargs)(args[0])
    return wrapper(*args, **kwargs)


"""
What follows is old code;
it appears that task behaviro customization can be performed either in 
something inserted between `shared_tas` and the task callable 
(see `pipeline_task_wrapper`), or in a subclass of `Task`.
Below is an implementation of the latter, but we have instead used
an implementation of the former.
"""

#class StateTrackingTask(Task):
#    """Task type that provides state tracking for chains.
#    Requires use of [other wrapper]; this base class handles
#    tasks that are being *passed* a result from a previous task
#    in the chain, we still need a way to *pass* a result to the
#    next task in the chain.
#
#    TODO:
#        - we assume that tasks are called in a chain, this should
#        be verified.
#    """
#    def __call__(self, *args, **kwargs):
#        # need to pop the return value of the previous task, if there is one,
#        # and store it in the chain state
#        #if not hasattr(self, '_pipeline_chain_state'):
#        #    self._pipeline_chain_state = StateTracker()
#
#        # unsure why this is here
#        #args = args[1:]
#
#
#
#        # store the result of the last-executed task (if one) into self.
#        # we need to rely on the system to make sure that a task that
#        # comes in with no args (but having a state) truly is the first task in a chain,
#        # and it should already have a build context provided to it
#        # by the executor.
#        # if len(args) > 1:
#        #     # I use type().__name__ here to reduce coupling
#        #     # and avoid circular imports.
#        #     if isinstance(args[0], StateTracker):
#        #         # means we are a non-zeroth element in a chain,
#        #         # and the pipeline task wraper has leveraged mutable
#        #         # signatures to pass the build context to us.
#        #         self._pipeline_chain_state['build_context'] = args[0]
#        #         args = args[1:]
#
#        return super(StateTrackingTask, self).__call__(*args, **kwargs)



