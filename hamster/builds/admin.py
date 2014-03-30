from django.contrib import admin
from .models import Build, Artifact


class BuildAdmin(admin.ModelAdmin):
    pass
admin.site.register(Build, BuildAdmin)


class ArtifactAdmin(admin.ModelAdmin):
    pass
admin.site.register(Artifact, ArtifactAdmin)
