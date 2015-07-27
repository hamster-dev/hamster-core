"""
conftest.py

py.test hook file
"""
import os
from django import setup
from celery import Celery

class Config:
    CELERY_ALWAYS_EAGER = True

app = Celery()
app.config_from_object(Config)

def pytest_configure():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hamster.local_settings')
    setup()