import pytest

"""
FUUUUUUUUUCK
If any test uses scoped_broker, it fucks up the entirety of 
integration tests if you want to connect to a broker
"""
@pytest.fixture
def scoped_broker():
    """Fixture that privides a locally-scoped Celery broker.
    The app exposed will never be accessible to celery,
    so you cannot run a test using this fixture connected to
    a real broker.
    """
    from celery import Celery

    class Config:
        BROKER_URL = ''
        CELERY_RESULT_BACKEND = ''
        CELERY_ALWAYS_EAGER = True

    app = Celery()
    app.config_from_object(Config)
    return app

# note: this is part of the TODO from integration/__init__.py
#def pytest_addoption(parser):
#    parser.addoption(
#        "--broker",
#        help="run tests using a broker"
#    )

