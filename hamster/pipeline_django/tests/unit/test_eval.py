import pytest

from pipeline_django.models import EventHandler

class Source(object):
    pass

def test_config_eval():

    source = Source()
    setattr(source, 'test', 'qwerty')
    assert EventHandler.evaluate(
        {'source': source},
        ['source.test', 'is', 'qwerty']
    )
    assert not EventHandler.evaluate(
        {'source': source},
        ['source.test', 'is', 'sqwerty']
    )
    assert EventHandler.evaluate(
        {'source': source},
        ['source.test', 'in', ['qwerty']]
    )
    assert EventHandler.evaluate(
        {'source': source},
        ['source.test', 'in', ['qwerty', 'uiop']]
    )
    assert not EventHandler.evaluate(
        {'source': source},
        ['source.test', 'in', ['qwert', 'uiop']]
    )
    assert EventHandler.evaluate(
        {'source': source},
        ['source.test', 'like', 'qwerty']
    )
    assert EventHandler.evaluate(
        {'source': source},
        ['source.test', 'like', '.werty']
    )
    assert EventHandler.evaluate(
        {'source': source},
        ['source.test', 'like', '.*wert.*']
    )
    assert EventHandler.evaluate(
        {'source': source},
        ['source.test', 'like', '.wert.']
    )
    assert EventHandler.evaluate(
        {'source': source},
        ['source.test', 'like', '[q]werty']
    )
    assert EventHandler.evaluate(
        {'source': source},
        ['source.test', 'like', '^qwerty$']
    )
    assert not  EventHandler.evaluate(
        {'source': source},
        ['source.test', 'like', '^qwert$']
    )
    assert not  EventHandler.evaluate(
        {'source': source},
        ['source.test', 'like', '..werty']
    )
    with pytest.raises(NotImplementedError):
        EventHandler.evaluate(
            {'source': source},
            ['source.test', 'boom', 'x']
        )