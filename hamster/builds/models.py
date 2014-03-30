from django.db import models
from jobs.models import Job


class Build(models.Model):
    BUILD_ERROR = 'E'
    BUILD_FAILED = 'F'
    BUILD_SUCCESS = 'S'
    BUILD_STATUS = (
        (BUILD_ERROR, 'Error'),
        (BUILD_FAILED, 'Failed'),
        (BUILD_SUCCESS, 'Success')
    )

    job = models.ForeignKey(Job)
    executed_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=1, choices=BUILD_STATUS)
    commit = models.CharField(max_length=80)
    duration = models.IntegerField(blank=True)
    output = models.TextField(blank=True)

    @property
    def build_number(self):
        builds = Build.objects.filter(job=self.job)
        return list([b.id for b in builds]).index(self.id) + 1

    def __unicode__(self):
        return "{}-#{}".format(self.job.name, self.build_number)


class Artifact(models.Model):
    build = models.ForeignKey(Build)
    artifact = models.FileField(upload_to="artifacts/%Y/%m/%d")

    def __unicode__(self):
        return self.artifact
