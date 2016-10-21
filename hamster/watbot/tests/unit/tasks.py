"""
Best-practices for task unit testing in a django app.

1. Define your tasks within the test folder.
2. Since I may not be testing the pipeline task types,
I can just use shared_task from celery (only as long as I dont enter
into any pipeline code paths)
"""
from celery import shared_task

@shared_task
def dummy(*args, **kwargs):
    return 'dummy'
