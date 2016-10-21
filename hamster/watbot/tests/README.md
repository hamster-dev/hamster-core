Running tests:
Must run from within the `hamster` app directory

    cd hamster
    # all the tests
    pytest event/tests  --ds event.tests.settings

    # one test module
    pytest event/tests/unit/test_klasses.py  --ds event.tests.settings

    # one test function
    pytest event/tests/unit/test_klasses.py  --ds event.tests.settings -k test_function

    # runnning with broker - need to provide broker url in env var
    PIPELINE_TEST_USE_BROKER=redis://localhost/0 celery -A event.tests.integration worker -l debug
    PIPELINE_TEST_USE_BROKER=redis://localhost/0 pytest event/tests/integration --ds event.tests.settings
