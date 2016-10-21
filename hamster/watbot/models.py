from django.db import models


class WatTracker(models.Model):
    """Model to track amount of wats for a given pull request.
    """
    org = models.CharField(max_length=64)
    repo = models.CharField(max_length=64)
    number = models.IntegerField()
    watcnt = models.IntegerField()

    class Meta:
        app_label = 'watbot'
        unique_together = ('org', 'repo', 'number')
