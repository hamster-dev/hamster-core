Running tests:
Must run from within the `hamster` app directory

    cd hamster
    # all the tests
    pytest hookshot/tests  --ds hookshot.tests.settings

    # one test module
    pytest hookshot/tests/unit/test_klasses.py  --ds hookshot.tests.settings

    # one test function
    pytest hookshot/tests/unit/test_klasses.py  --ds hookshot.tests.settings -k test_function

    # runnning with broker - need to provide broker url in env var
    PIPELINE_TEST_USE_BROKER=redis://localhost/0 celery -A hookshot.tests.integration worker -l debug
    PIPELINE_TEST_USE_BROKER=redis://localhost/0 pytest hookshot/tests/integration --ds hookshot.tests.settings
