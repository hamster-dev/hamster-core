from django.contrib import admin
from pipeline_django.models import PipelineEventHandler


class PipelineEventHandlerAdmin(admin.ModelAdmin):
    pass


admin.site.register(PipelineEventHandler, PipelineEventHandlerAdmin)