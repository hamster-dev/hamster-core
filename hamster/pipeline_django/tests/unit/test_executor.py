import pytest

from pipeline.actions import (
    action, TaskResult
)

from pipeline.models import EventHandler
from pipeline.executor import Executor

import logging
logger = logging.getLogger(__name__)



@action(called=False)
def task_action_one(self, context, **kwargs):
    self.called = True
    self.source_was = context.source
    self.parent_was = context.parent
    return context.update(self, TaskResult(True, output='action_one'))

@action(called=False)
def task_action_two(self, context, **kwargs):
    self.called = True
    self.source_was = context.source
    self.parent_was = context.parent
    return context.update(self, TaskResult(True, output='action_two'))

@action(called=False)
def task_action_two_err(self, context, **kwargs):
    self.called = True
    self.source_was = context.source
    self.parent_was = context.parent
    return context.update(self, TaskResult(False, output='action_two'))

@action(called=False)
def task_action_three(self, context, **kwargs):
    self.called = True
    self.source_was = context.source
    self.parent_was = context.parent
    return context.update(self, TaskResult(True, output='action_three'))

@action(called=False)
def task_action_one_callback(self, context, **kwargs):
    self.called = True
    self.source_was = context.source

@action(called=False)
def task_action_one_errback(self, context, **kwargs):
    self.called = True
    self.source_was = context.source

@action(called=False)
def task_action_two_callback(self, context, **kwargs):
    self.called = True
    self.source_was = context.source

@action(called=False)
def task_action_two_errback(self, context, **kwargs):
    self.called = True
    self.source_was = context.source

@action(called=False)
def task_action_three_callback(self, context, **kwargs):
    self.called = True
    self.source_was = context.source

@action(called=False)
def task_action_three_errback(self, context, **kwargs):
    self.called = True
    self.source_was = context.source

class TestExecutor:

    def test_simple_chain(self):
        config = EventHandler()
        config.actions = [
            {
                "task": "task_action_one",
            },
            {
                "task": "task_action_two",
            },
            {
                "task": "task_action_three",
            }
        ]
        actions = config.get_actions()
        source = 42
        executor = Executor()

        returned_build_context = executor.schedule(actions, source).get()

        assert task_action_one.called
        assert task_action_one.source_was == 42
        assert task_action_one.parent_was is None

        assert task_action_two.called
        assert task_action_two.source_was == 42
        assert isinstance(task_action_two.parent_was, TaskResult)
        assert task_action_two.parent_was.output == 'action_one'

        assert task_action_three.called
        assert task_action_three.source_was == 42
        assert isinstance(task_action_three.parent_was, TaskResult)
        assert task_action_three.parent_was.output == 'action_two'

        assert isinstance(returned_build_context.last, TaskResult)
        assert returned_build_context.parent.output == \
               returned_build_context.last.output == 'action_three'

    def test_simple_chain_with_failure(self):
        """Test that a chain with a failure within it still continues.
        This behavior will change iwth milestone 3.
        """
        config = EventHandler()
        config.actions = [
            {
                "task": "task_action_one",
            },
            {
                "task": "task_action_two_err",
            },
            {
                "task": "task_action_three",
            }
        ]
        actions = config.get_actions()
        source = 42
        executor = Executor()

        returned_build_context = executor.schedule(actions, source).get()

        assert task_action_one.called
        assert task_action_one.source_was == 42
        assert task_action_one.parent_was is None

        assert task_action_two_err.called
        assert task_action_two_err.source_was == 42
        assert isinstance(task_action_two_err.parent_was, TaskResult)
        assert task_action_two_err.parent_was.output == 'action_one'

        assert task_action_three.called
        assert task_action_three.source_was == 42
        assert isinstance(task_action_three.parent_was, TaskResult)
        assert task_action_three.parent_was.return_value == False
        assert task_action_three.parent_was.output == 'action_two'

        assert isinstance(returned_build_context.last, TaskResult)
        assert returned_build_context.last.output == 'action_three'

    @pytest.mark.xfail(reason='child tasks are currently broken')
    def test_chain_with_callback(self):
        config = EventHandler()
        config.actions = [
            {
                "task": "task_action_one",
                "success_handler": {
                    "task": "task_action_one_callback",

                },
                "failure_handler": {
                    "task": "task_action_one_errback",

                }
            },
            {
                "task": "task_action_two",
            },
            {
                "task": "task_action_three",
            }
        ]
        actions = config.get_actions()
        source = 42
        executor = Executor()

        ret = executor.schedule(actions, source).get()

        assert task_action_one.called
        assert task_action_one.source_was == 42
        assert task_action_one.parent_was is None

        assert task_action_one_callback.called
        assert task_action_one_callback.source_was == 42
        assert isinstance(task_action_one_callback.parent_was, TaskResult)
        assert task_action_one_callback.parent_was.output == 'action_one'

        assert not task_action_one_errback.called

        assert task_action_two.called
        assert task_action_two.source_was == 42
        assert isinstance(task_action_two.parent_was, TaskResult)
        assert task_action_two.parent_was.output == 'action_one'

        assert task_action_three.called
        assert task_action_three.source_was == 42
        assert isinstance(task_action_three.parent_was, TaskResult)
        assert task_action_three.parent_was.output == 'action_two'

        assert isinstance(ret, TaskResult)
        assert ret.output == 'action_three'

    @pytest.mark.xfail(reason='child tasks are currently broken')
    def test_chain_with_call_and_errbacks(self):
        """Test chain plus callback/errback execution where there is a failure."""
        config = EventHandler()
        config.actions = [
            {
                "task": "task_action_one",
                "success_handler": {
                    "task": "task_action_one_callback",

                },
                "failure_handler": {
                    "task": "task_action_one_errback",

                }
            },
            {
                "task": "task_action_two_err",
                "success_handler": {
                    "task": "task_action_two_callback",

                },
                "failure_handler": {
                    "task": "task_action_two_errback",

                }
            },
            {
                "task": "task_action_three",
                "success_handler": {
                    "task": "task_action_three_callback",

                },
                "failure_handler": {
                    "task": "task_action_three_errback",

                }
            }
        ]
        actions = config.get_actions()
        source = 42
        executor = Executor()

        ret = executor.schedule(actions, source).get()

        assert task_action_one.called
        assert task_action_one.source_was == 42
        assert task_action_one.parent_was is None

        assert task_action_one_callback.called
        assert task_action_one_callback.source_was == 42
        assert isinstance(task_action_one_callback.parent_was, TaskResult)
        assert task_action_one_callback.parent_was.output == 'action_one'

        assert not task_action_one_errback.called

        assert task_action_two_err.called
        assert task_action_two_err.source_was == 42
        assert isinstance(task_action_two_err.parent_was, TaskResult)
        assert task_action_two_err.parent_was.output == 'action_one'

        assert task_action_two_errback.called
        assert task_action_two_errback.source_was == 42
        assert isinstance(task_action_two_errback.parent_was, TaskResult)
        assert task_action_two_errback.parent_was.output == 'action_two'

        assert not task_action_two_callback.called

        assert task_action_three.called
        assert task_action_three.source_was == 42
        assert isinstance(task_action_three.parent_was, TaskResult)
        assert task_action_three.parent_was.output == 'action_two'

        assert task_action_three_callback.called
        assert task_action_three_callback.source_was == 42
        assert isinstance(task_action_three_callback.parent_was, TaskResult)
        assert task_action_three_callback.parent_was.output == 'action_three'

        assert not task_action_three_errback.called

        assert isinstance(ret, TaskResult)
        assert ret.output == 'action_three'