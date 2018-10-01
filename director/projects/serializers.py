from rest_framework import serializers

from .models import Project, Source, FileSource


class SourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Source
        fields = ('id', 'type', 'path')


class FileSourceSerializer(serializers.ModelSerializer):
    class Meta():
        model = FileSource
        fields = ('file', 'updated')


class ProjectSerializer(serializers.ModelSerializer):
    sources = SourceSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = ('id', 'name', 'description', 'sources')
