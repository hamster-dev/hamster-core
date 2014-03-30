from .models import Build, Artifact
from rest_framework import serializers


class BuildSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Build
        fields = ('url', 'status', 'commit', 'duration',
                'executed_at', 'output')
