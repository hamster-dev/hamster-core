"""
conftest.py

py.test hook file
"""
import os
import json
import pytest
from django import setup
from celery import Celery

class Config:
    CELERY_ALWAYS_EAGER = True

app = Celery()
app.config_from_object(Config)

#TODO: figure out how to import fixtures, they are duplicated
# for unit and int tests
FIXTURES_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

@pytest.fixture
def pullrequest_hook_open_json():
    """Returns a json string for pr open webhook
    """
    pth = os.path.join(
        FIXTURES_BASE,
        'fixtures', 'webhooks', 'json', 'pr-opened.json'
    )
    with open(pth, 'r') as fh:
        data = fh.read()

    return data

@pytest.fixture
def pullrequest_hook_open_form():
    """Returns a json string for pr open webhook when sent as
    form content type
    """
    pth = os.path.join(
        FIXTURES_BASE,
        'fixtures', 'webhooks', 'x-www-form-urlencoded', 'pr-opened.json'
    )
    with open(pth, 'r') as fh:
        data = fh.read()

    return data

@pytest.fixture
def pullrequest_hook_open_data():
    """Returns a json string for pr open webhook
    """
    pth = os.path.join(
        FIXTURES_BASE,
        'fixtures', 'webhooks', 'json', 'pr-opened.json'
    )
    with open(pth, 'r') as fh:
        data = fh.read()

    return json.loads(data)

@pytest.fixture
def pullrequest_source():
    """Returns dict created from the
    test json provided by github in the api documentation
    suitable t be loaded into a pullrequest_source.
    """
    pth = os.path.join(
        FIXTURES_BASE,
        'fixtures', 'pull_request.json'
    )
    with open(pth, 'r') as fh:
        data = fh.read()

    return json.loads(data)

def pytest_configure():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hamster.local_settings')
    setup()