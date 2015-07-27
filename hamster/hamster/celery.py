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


app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

