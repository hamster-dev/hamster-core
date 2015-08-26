#TODO: support integration tests running out of eager mode, with broker


from . import tasks

import pytest

@pytest.fixture
def scoped_broker():
    """Fixture that privides a locally-scoped Celery broker."""
    from celery import Celery

    class Config:
        BROKER_URL = ''
        CELERY_RESULT_BACKEND = ''
        CELERY_ALWAYS_EAGER = True

    app = Celery()
    app.config_from_object(Config)
    return app