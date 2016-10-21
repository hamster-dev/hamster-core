import re
import sys

__all__ = ['matcher', 'safe_eval', 'evaluate_criteria', 'evaluate_single_criterion']


ALLOWED_BUILTINS = ('bool',)


class Registry(type):
    """Simple implementation of the Registry pattern using the
    declarative style.
    Classes that wish to implement a registry should utilize this as
    their metaclass.
    Subclasses of registries ("registered classes" should define the
    class attribute `__id`, which will serve as their key in the registry.
    Subclasses of registries that do not define an `__id` are considered
    'abstract', and will not be added to the registry.
    Their purpose should only be to serve to facilitate OOP patterns.
    """
    def __init__(cls, name, bases, nmspc):
        super(Registry, cls).__init__(name, bases, nmspc)
        if not hasattr(cls, '_registry'):
            # assume base type here (superclass), which has no instances,
            # only implementations.
            cls._registry = {}
            return
        _id = '_{}__id'.format(name)
        if hasattr(cls, _id):
            cls._registry[getattr(cls, _id)] = cls  # noqa
            #pass
        else:
            # this is an unnamed entry, just give it a unique name
            cls._registry[id(cls)] = cls

    def factory(cls, name, *args, **kwargs):
        """Return an instance of the registered Thing identified by ``name``."""
        klass = cls.get(name)
        if not klass:
            raise KeyError('{} having name {} not found'.format(cls, name))
        return klass(*args, **kwargs)

    def get(cls, name):
        """Return a registred subclass by it's __id."""
        return cls._registry.get(name)

    def getlist(cls):
        """Return all the subclasses registered for a given class.
        """
        return filter(
            lambda k: issubclass(k, cls),
            cls._registry.values()
        )

    def find(cls, attr, value):
        """Find registered subclasses that define the attribute `attr`
        which has the value ``value``.
        """
        available = cls.getlist()
        found = []
        for v in available:
            if hasattr(v, attr) and getattr(v, attr) == value:
                found.append(v)
        return found

    def purge(cls):
        """Remove all entries from a registry.
        """
        cls._registry = {}

class Matcher(metaclass=Registry):
    """Base class for a criteria matcher.
    """
    def __call__(self, data):
        """Determine if `data` meets some expectations.
        :param data: data to use in match
        :returns: bool
        """
        raise NotImplementedError


def get_default_builtins():
    """Get the allowed eval() builtins.
    """
    ret = {}
    for k, v in __builtins__.items():
        if k in ALLOWED_BUILTINS:
            ret[k] = v
    return ret


def safe_eval(expression, _locals, _globals=None):
    """Run eval in a semi-safe manner.

    Current impl just runs eval().  Future iterations will attempt to
    do this in a safer manner, using ast.
    see: http://code.activestate.com/recipes/364469-safe-eval/
    """
    if not _globals:
         _globals = {'__builtins__': get_default_builtins()}

    _locals = _locals or {}

    # `expression` might just be a string, so catch some exceptions here
    # and just return expression.
    try:
        ret = eval(
            expression,
            _globals,
            _locals
        )
    except NameError:
        return expression
    except Exception as ex:
        print('err in eval of {}: {}'.format(expression, ex), file=sys.stderr)
        raise
        return expression
    return ret


def evaluate_single_criterion(data, criterion):
    """Determine if a one of criteria match the event data.
    This is a very, very trivial implementation of something
    that could be interesting, if given time to hack on it.

    An example of criteria is:
        ['object.attribute', 'is', 'some value']

    :param data: dict of event, source
    :param criterion: 3-tuple of (lvalue, operator, rvalue)
    :returns boolean
    """
    oper = criterion[1]
    try:
        lvalue = safe_eval(criterion[0], data)
    except:
        #TODO
        raise
    rvalue = criterion[2]

    if oper == 'is':
        return lvalue == rvalue
    elif oper == 'in':
        return lvalue in rvalue
    elif oper == 'like':
        #TODO re.flags?
        return bool(re.search(
            rvalue, lvalue
        ))
    elif oper == 'not':
        return lvalue != rvalue
    elif oper == 'not in':
        return lvalue not in rvalue
    elif oper == 'not like':
        #TODO re.flags?
        return not bool(re.search(
            rvalue, lvalue
        ))
    elif oper == "matches":
        # custom criteria matching
        matcher_klass = Matcher.get(rvalue)
        if not matcher_klass:
            raise NotImplementedError(
                'matcher {} not found'.format(rvalue)
            )
        return matcher_klass()(lvalue)
    else:
        raise NotImplementedError(
            'operator {} not supported'.format(oper)
        )


def evaluate_criteria(data, criteria):
    """Check to see if the criteria matches data.

    - if criteria is None, it should always match
    - if criteria is [], it should never match
    - otherwise, evaluate against deserialized incoming data

    :returns: bool
    """
    if criteria is None:
        return True

    assert isinstance(criteria, (list, tuple))
    if not len(criteria):
        return False

    for criterion in criteria:
        if not evaluate_single_criterion(data, criterion):
            return False

    return True
