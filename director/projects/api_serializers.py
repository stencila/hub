from rest_framework import serializers
from rest_framework.fields import JSONField

from projects.project_models import Project, ProjectEvent


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'account', 'name']


class ProjectEventSerializer(serializers.ModelSerializer):
    log = JSONField()
    project = ProjectSerializer()

    class Meta:
        model = ProjectEvent
        fields = ['id', 'started', 'finished', 'message', 'success', 'project', 'event_type', 'log']
