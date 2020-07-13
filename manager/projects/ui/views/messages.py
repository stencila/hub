"""
A module for generating project related messages to users.

This is intended to be used across most project related views to
notify the user of potential limits (e.g. approaching maximum job limits)
"""
import datetime
from typing import List

from django.contrib import messages
from django.http import HttpRequest
from django.template.loader import render_to_string

from manager.helpers import should_send_message
from projects.models.projects import Project


def all_messages(request: HttpRequest, project: Project, exclude: List[str] = []):
    """
    Generate all messages for a project (except those listed in `exclude`).
    """
    if "temporary_project" not in exclude:
        temporary_project(request, project)


def temporary_project(request: HttpRequest, project: Project):
    """
    Warn the user that this is a temporary project and that they can claim it.
    """
    if project.temporary and should_send_message(
        request,
        "temporary_project_{}".format(project.name),
        datetime.timedelta(minutes=1),
    ):
        messages.warning(
            request,
            render_to_string(
                "projects/messages/temporary_project.html",
                dict(project=project, deletion_time=project.scheduled_deletion_time),
            ),
            extra_tags="stay safe",
        )
