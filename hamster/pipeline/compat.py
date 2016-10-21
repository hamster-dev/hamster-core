from base64 import b64encode, b64decode
from json import dumps, loads, JSONEncoder
import pickle


class PythonObjectEncoder(JSONEncoder):
    """py3-specific.
    py2 is here:
        http://stackoverflow.com/questions/8230315/python-sets-are-not-json-serializable
    """
    def default(self, obj):
        if isinstance(obj, (list, dict, str, int, float, bool, type(None))):
            return super().default(obj)
        return {'_python_object': b64encode(pickle.dumps(obj)).decode('utf-8')}


def as_python_object(dct):
    if '_python_object' in dct:
        return pickle.loads(b64decode(dct['_python_object'].encode('utf-8')))
    return dct


def wtf_dumps(obj):
    return dumps(obj, cls=PythonObjectEncoder)


def wtf_loads(obj):
    return loads(obj, object_hook=as_python_object)
