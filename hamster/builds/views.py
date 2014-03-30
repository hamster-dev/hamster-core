from django.shortcuts import render

from rest_framework import viewsets
from .models import Build
from .serializers import BuildSerializer


class BuildViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows builds to be viewed or edited.
    """
    queryset = Build.objects.all()
    serializer_class = BuildSerializer
