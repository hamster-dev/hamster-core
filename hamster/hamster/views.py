from django.http import HttpResponse
from hamster.celery import debug_task


def home(request):
    result = debug_task.delay()
    print result.get()
    return HttpResponse("Hello world")
