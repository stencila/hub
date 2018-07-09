from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.generic import View

from .models import (
    Project
)


class ProjectArchiveView(View):

    def get(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)

        archive = project.pull()
        body = archive.getvalue()

        response = HttpResponse(body, content_type='application/x-zip-compressed')
        response['Content-Disposition'] = 'attachment; filename={}.zip'.format('project.name')
        return response

    def put(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)

        archive = request.body
        project.push(archive)

        response = HttpResponse()
        return response
