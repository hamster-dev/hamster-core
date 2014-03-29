from .models import Job
from rest_framework import serializers


class JobSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Job
        fields = ('url', 'job_name', 'disabled')
