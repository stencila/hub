# flake8: noqa F401
from django.contrib import admin

from .project_admin import (
    ProjectAdmin,
    ProjectPermissionAdmin,
    ProjectRoleAdmin,
    ProjectAgentRoleAdmin,
)
from .session_admin import SessionAdmin, SessionParametersAdmin, SessionRequestAdmin
from .source_admin import SourceAdmin

from .models import Node, Snapshot


@admin.register(Node)
class NodeAdmin(admin.ModelAdmin):
    list_display = ["id", "key", "creator", "created", "project", "app", "host"]
    list_select_related = ["creator", "project"]
    list_filter = ["app"]
    show_full_result_count = False

    def get_queryset(self, request):
        """Get custom queryset that does not fetch the `json` field (which can be large)."""
        queryset = super().get_queryset(request)
        return queryset.defer("json")


@admin.register(Snapshot)
class SnapshotAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "project",
        "version_number",
        "tag",
        "creator",
        "created",
        "completed",
    ]
    list_select_related = ["creator", "project"]
