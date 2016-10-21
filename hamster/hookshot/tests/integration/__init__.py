"""
Integration tests can optionally have a broker configured.
Unit tests should use a scoped_broker, or no broker.
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
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hookshot.tests.settings')
    # calling this function with no params will pull the broker url from the envirnment
    app = make_test_app()
