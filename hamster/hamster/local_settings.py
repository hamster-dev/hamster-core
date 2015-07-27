from __future__ import absolute_import
from hamster.settings import *

DEBUG = True
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(os.path.dirname(BASE_DIR), 'hamster.sqlite3'),
    }
}

FIXTURE_DIRS = (
    os.path.join(BASE_DIR, 'pipeline', 'tests', 'fixtures'),
)

BROKER_URL = CELERY_RESULT_BACKEND = 'redis://localhost:6380/0'

# # this doesnt appear to work.  using global setting instead
# ^^^ it totally works.  but do i need it??  commenting.
# PIPELINE_TASK_TIMEOUT = 2
# CELERYD_TASK_TIME_LIMIT = PIPELINE_TASK_TIMEOUT

# see hamster/celery.py for impl
# CELERY_ACCEPT_CONTENT = ['betterjson']
# CELERY_RESULT_SERIALIZER = CELERY_TASK_SERIALIZER = 'betterjson'


PIPELINE_TEST_EAGER = True

