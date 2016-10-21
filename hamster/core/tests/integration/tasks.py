"""
Best-practices for task testing in a django app.

1. Define your tasks within the test folder.
2. Since I may not be testing the pipeline task types,
I can just use shared_task from celery.
3. Make sure that your tests/tasks.py file is NEVER imported outside
of the tests, or else they will pollute your app and may even override 
any existing tasks that have the same names



# Best practice:
    #   - keep all your tests tasks in a single file in the tests module.
    #   1. you will need to import the tasks in order for the worker to find them
    #   2. It i easier to not duplicate task names.  This is important,
    #   because celery keeps globa state and it is (as far as I can tell)
    #   impossible to scope test tasks to the test module (just like we always
    #   want to scope test-related Things to the test itsrlf, so that they dont
    #   leak into other test files.
    #


If your app has its own tasks that you want to test, you need to do this:
    app.autodiscover_tasks(['tests.integration']) in either tests/settings.py or __init__.py or conftest.py

Also, make sure that your tests module is not importable  there cannot be a tests/__init__.py
"""
from pipeline.pipeline import state_aware_task

@state_aware_task
def echo(arg):
    return arg


@state_aware_task
def echo_again(arg):
    return arg


@state_aware_task
def nothing():
    return None
