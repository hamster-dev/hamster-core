from boltons.typeutils import classproperty
from pipeline.gtfo import Registry

class Bot(metaclass=Registry):

    @property
    def tasks(cls):
        return []  # list of configured `core.pipeline.Task`s
