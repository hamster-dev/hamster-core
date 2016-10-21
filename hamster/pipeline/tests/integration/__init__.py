"""
This logic is in __init__.py and not settings.py, as it has
to be importable if you want to ever run the tests inside a real broker
in non-eager mode.
"""
import os
import celery
from pipeline.utils import make_test_app
from . import tasks


# if there is no celery app defined, create one.
# this allows us to define an app for this module only,
# or alternatively define an app for the entire project
# so we can run the whole test suite with the same app
if celery.current_app.main != 'hamster-test':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pipeline.tests.settings')
    # calling this function with no params will pull the broker url from the envirnment
    app = make_test_app()
