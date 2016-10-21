import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hamster.settings')
app = Celery('hamster')
#
# Below is WIP for json serialization. Currently using pickle.
# TODO add link to relevant gh issue here
#
# import json
# from datetime import datetime, date
# from decimal import Decimal
#
# # We need a custom serializer to handle date and datetime objects.
# class JSONSerializer(json.JSONEncoder):
#     def default(self, data):
#         if isinstance(data, (date, datetime)):
#             return data.isoformat()
#         elif isinstance(data, Decimal):
#             return float(data)
#
#         elif data.__class__.__name__ == "PullRequest":
#             return data.__dict__
#         raise TypeError("Unable to serialize %r (type: %s)" % (data, type(data)))
#
#
# def my_dumps(obj):
#     return json.dumps(obj, cls=JSONSerializer)
#
#
# from kombu.serialization import register
# register(
#     'betterjson',
#     my_dumps,
#     json.loads,
#     content_type='application/x-myjson',
#     content_encoding='utf-8')
class BrokerlessConfig:
    BROKER_URL = ''
    CELERY_RESULT_BACKEND = ''
    CELERY_ALWAYS_EAGER = True
class TestSerializerConfig:
    BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
    CELERY_ALWAYS_EAGER = False
    CELERY_ACCEPT_CONTENT = ['json', 'pickle', 'application/x-wtfcelery'] #, 'application/x-python-serialize']
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'

app.config_from_object('django.conf:settings')
#app.config_from_object(TestSerializerConfig)
#app.config_from_object(BrokerlessConfig)

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

from pipeline.compat import wtf_dumps, wtf_loads
from kombu.serialization import register
register('myjson', wtf_dumps, wtf_loads,
         content_type='application/x-wtfcelery',
         content_encoding='utf-8')

