from django.contrib import admin
from pipeline_django.models import EventSubscriber, Pipeline


class PipelineAdmin(admin.ModelAdmin):
    pass

class EventSubscriberAdmin(admin.ModelAdmin):
    pass

admin.site.register(Pipeline, PipelineAdmin)
admin.site.register(EventSubscriber, EventSubscriberAdmin)
