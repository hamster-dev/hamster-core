"""
This file is required for celery to serialize tasks initiated during tests.
Do not import *anything* here, or else you will pollute runtime with your
test tasks.
"""
