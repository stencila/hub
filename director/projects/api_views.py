from django.shortcuts import get_object_or_404
from rest_framework import generics, status, parsers, views
from rest_framework.response import Response

from .models import Project, Source
from .serializers import ProjectSerializer, SourceSerializer, FileSourceSerializer


class ProjectRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class ProjectSourceListAPIView(generics.ListAPIView):
    serializer_class = SourceSerializer

    def get_queryset(self):
        pk = self.kwargs['pk']
        return Source.objects.filter(project=pk)


class ProjectSourceRetrieveDestroyAPIView(generics.RetrieveDestroyAPIView):
    serializer_class = SourceSerializer

    def get_object(self):
        pk = self.kwargs['pk']
        source = self.kwargs['source']
        return get_object_or_404(Source, id=source, project=pk)


class ProjectFileSourceCreateAPIView(views.APIView):
    parser_classes = (parsers.MultiPartParser, parsers.FormParser)

    def post(self, request, pk):
        file_serializer = FileSourceSerializer(data=request.data)
        if file_serializer.is_valid():
            filesource = file_serializer.save()
            filesource.project = Project.objects.get(pk=pk)
            filesource.save()
            return Response(file_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
