"""
conftest.py

py.test hook file
"""
import os
import json
import pytest


FIXTURES_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Note the lack of pytest_configure, it is on purpose.
# The import of tasks in tests/integration/__init__.py (
# which is required for the worker to discover the testing tasks)
# causes a recursion in pytest_configure.  So, in order to run integration
# tests you must manually provide DJANGO_SETTINGS_MODULE.
# Celery config for the integration tests can be found in
# integration/__init__.py, so it is discoverable by the worker.
# For now, I havent figured out how to make a test-specific worker,
# so we need to use the global hamster worker.  This means that tests
# cannot define their own test-related tasks.
# To start the worker, run
# > cd hamster
# > DJANGO_SETTINGS_MODULE=hamster.local_settings celery -A hamster worker -l debug
# Note that you must export the HAMSTER_* environment variables into the worker's
# process so that it can connect to github.


@pytest.fixture
def pullrequest_hook_open_data():
    """Returns a json string for pr open webhook
    """
    pth = os.path.join(
        FIXTURES_BASE,
        'fixtures', 'webhooks', 'pullrequest.opened.json'
    )
    with open(pth, 'r') as fh:
        data = fh.read()

    return json.loads(data)


@pytest.fixture
def pullrequestcomment_hook_create_data():
    """Returns a json string for pullrequest issue comment webhook
    """
    pth = os.path.join(
        FIXTURES_BASE,
        'fixtures', 'webhooks', 'pullrequest_comment.created.json'
    )
    with open(pth, 'r') as fh:
        data = fh.read()

    return json.loads(data)


@pytest.fixture
def pullrequestcomment_hook_prbuilder_success_data():
    """Returns a json string for pullrequest issue comment webhook
    """
    pth = os.path.join(
        FIXTURES_BASE,
        'fixtures', 'webhooks', 'prbuilder_status.succeeded.json'
    )
    with open(pth, 'r') as fh:
        data = fh.read()

    return json.loads(data)


'''
 Removed code here
'''
# This was for starting the worker as a fixture.
# However, the worker requires the virtualenv, and pytest-xprocess
# does not have access to it.
# TODO: figure out how to make this work, since it will simplify testing.
# @pytest.fixture
# def celery_broker(xprocess):
#     try:
#         os.environ['HAMSTER_TEST_USE_BROKER']
#     except KeyError:
#         return False
#
#     def preparefunc(cwd):
#         import pytest; pytest.set_trace()
#         print(cwd)
#         return ('Server started', ['celery -A integration worker -l debug'])
#
#     logfile = xprocess.ensure("Server started", preparefunc)
#     return logfile  # redis.Redis()


# This was a triel of how to conditionally specifiy whether or not to run the
# broker under pytest.  It's a better idea to use tox, but I am keeping this
# here in case it pans out.  Once you do this, you can access the option
# in the putest_configure() function.
# def pytest_addoption(parser):
#     parser.addoption(
#         "--broker", action="store_true",
#         help="run with broker, must manually specify django settings"
#     )
