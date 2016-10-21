import os
from pipeline.utils import make_test_app

# create a celery app to be shared amongst all modules
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hamster.local_settings')
app = make_test_app('redis://localhost/0')

# import all of our modules tasks
# unit tests shouldnt have importable tasks
import hookshot.tests.integration
import core.tests.integration
import dt2.tests.integration
import pipeline.tests.integration
import pipeline.tasks
