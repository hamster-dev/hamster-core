from django.db import models

class Job(models.Model):
    job_name = models.CharField(max_length=80)
    disabled = models.BooleanField(default=False)

    def __unicode__(self):
        return self.job_name
