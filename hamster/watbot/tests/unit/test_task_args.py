import pytest
from event.task_args import (
        TaskArgument,
        LazyTaskArgument,
        TemplateTaskArgument,
    )


def test_namespaced_task_argument():
    """Test ``task_args.TaskArgument``
    """
    ta = TaskArgument('test.arg', 1)
    assert ta.name == 'arg'
    assert ta.stage == 'test'
    assert ta.value == 1
    assert ta.make_arg() == {'arg': 1}


def test_task_argument():
    """Test ``task_args.TaskArgument``
    """
    ta = TaskArgument('test_arg', 1)
    assert ta.name == 'test_arg'
    assert ta.stage == None
    assert ta.value == 1
    assert ta.make_arg() == {'test_arg': 1}


def test_lazy_task_argument():
    """Test ``task_args.LazyTaskArgument``
    """
    ta = LazyTaskArgument('test_arg', 'key')
    assert ta.name == 'test_arg'
    assert ta.stage == None
    assert ta.key == 'key'
    arg = ta.make_arg()
    assert 'test_arg' in arg
    assert len(arg) == 1
    assert type(arg['test_arg']).__name__ == 'LazyStateGetter'


def test_template_task_argument():
    """Test ``task_args.TemplateTaskArgument``
    """
    ta = TemplateTaskArgument('test_arg', 'hello')
    assert ta.name == 'test_arg'
    assert ta.stage == None
    assert ta.template == 'hello'
    arg = ta.make_arg()
    assert 'test_arg' in arg
    assert len(arg) == 1
    assert type(arg['test_arg']).__name__ == 'LazyTemplate'


def test_template_task_argument_bad_templ():
    """Test ``task_args.TemplateTaskArgument``
    """
    with pytest.raises(TypeError):
        ta = TemplateTaskArgument('test_arg', 1)
