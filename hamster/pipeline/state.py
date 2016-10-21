from jinja2 import Environment
from munch import Munch

import logging
logger = logging.getLogger(__name__)


class StateTracker(Munch):
    """Argument container.
    Is initially populated at task schedule time, and 
    updated after each task completes.
    Dictionary with keys for each task executed
    """
    def render_template(self, template, **kwargs):
        """Render a jinja template using current state.
        TODO: remove kwargs, its confusing and maybe not necessary,
            everything should be in the state tracker
        """
        #env = Environment()
        #env.globals.update(dict(self.items()))
        #env.globals.update(kwargs)
        #return env.from_string(template).render()
        return template


class LazyStateGetter(object):
    """Argument wrapper that will defer until
    task runtime and attempt to pull a value from
    StateTracker by key.
    """
    def __init__(self, key):
        self.key = key

    def rec_getattr(obj, attr):
        """Get object's attribute. May use dot notation.
        >>> class C(object): pass
	>>> a = C()
	>>> a.b = C()
	>>> a.b.c = 4
	>>> rec_getattr(a, 'b.c')
	4
	"""
        if '.' not in attr:
            return getattr(obj, attr)
        else:
            L = attr.split('.')
        return LazyStateGetter.rec_getattr(getattr(obj, L[0]), '.'.join(L[1:]))

    def extract(self, state):
        """Extract value from chain state"""
        #import ipdb; ipdb.set_trace()
        # Munch *should* support this, but it doesnt:
        #   > munchobj.a.b  # works!
        #  > getattr(muchobj, 'a.b')  # nope.

        return LazyStateGetter.rec_getattr(state, self.key)

class Template(object):
    def __init__(self, template):
        self.template = template
    def render(self, state):
        env = Environment()
        env.globals.update(state.items())
        return env.from_string(self.template).render()

class LazyTemplate(Template):
    pass

#class StateEvaluator(object):
#    """Argument wrapper that will defer until
#    task runtime nd will attempt to evaluate an
#    expression using StateTracker as globals.
#    """
#    def __init__(self, key):
#        self.key = key
#
#    def extract(self, state):
#        """Run eval using chain state"""
#        raise NotImplementedError


