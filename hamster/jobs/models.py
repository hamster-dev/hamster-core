from django.db import models

class Job(models.Model):
    name = models.CharField(max_length=80)
    disabled = models.BooleanField(default=False)
    project_url = models.URLField(blank=True)

    def __unicode__(self):
        return self.name
