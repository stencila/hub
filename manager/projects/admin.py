from django.contrib import admin

from projects.models.projects import Project, ProjectAgent
from projects.models.snapshots import Snapshot


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Admin interface for projects."""

    list_display = [
        "name",
        "account",
        "creator",
        "created",
        "temporary",
        "public",
    ]
    list_select_related = ["account", "creator"]


@admin.register(ProjectAgent)
class ProjectAgentAdmin(admin.ModelAdmin):
    """Admin interface for projects agents."""

    list_display = ["id", "project", "user_id", "team_id", "role"]
    list_select_related = ["project"]


@admin.register(Snapshot)
class SnapshotAdmin(admin.ModelAdmin):
    """Admin interface for project snapshots."""

    list_display = [
        "creator",
        "created",
    ]
    list_select_related = ["creator"]
