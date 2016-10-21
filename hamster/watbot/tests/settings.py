"""
Best-practices for testing a django app in isolation.

Issue: You will be testing the django app within the scope of a django *project*, which
will have a settings module, and a celery.py file.  This file is designed to set up a running
Celery instance that is connected to a broker.  However, for tests you do not want to connect
to a broker, and yo may not even want to run in eager mode.  Long story short: unit integration,
and functional tests will all require different Celery App configuration.  Because the Celery pp 
configuration is driven by settings module, each of these tests will require their own settings
module that is distinct from the django project's settings module.  using pytest-django, you can
provide a cli param to specify a settings module gfor each tyoe of test.

Testtypes: 
    unit - testing functions in isolation, mocking collaborators, and running celeyr app
    disconnected from a broker and in eager mode
    intehration - testing muktiple software componenets together, and will connect
    to collaborators instead of mock,  BUT system components will not be available.
    functional - re-running integration trests but using a live broker.

This file is just the basics required for bootstrapping a django install

Two broker strategies for unit tests:
    1. use an eager app, defined in this file
    2. use a scoped broker

    2. is easier.

     TODO:    what is benefit of 1?
"""
from hamster.local_settings import *
#import os
#
#SECRET_KEY = 'mike'
#DEBUG = True
#BASE_DIR = os.path.dirname(__file__)
#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': os.path.join(BASE_DIR, 'tests.sqlite3'),
#    }
#}
INSTALLED_APPS=('watbot', 'hookshot')  # required for migrations to run
