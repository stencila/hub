from django.contrib import admin
from polymorphic.admin import (
    PolymorphicChildModelAdmin,
    PolymorphicChildModelFilter,
    PolymorphicParentModelAdmin,
)

from projects.models.files import File
from projects.models.nodes import Node
from projects.models.projects import Project, ProjectAgent, ProjectEvent
from projects.models.snapshots import Snapshot
from projects.models.sources import (
    ElifeSource,
    GithubSource,
    GoogleDocsSource,
    Source,
    UploadSource,
    UrlSource,
)


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


@admin.register(ProjectEvent)
class ProjectEventAdmin(admin.ModelAdmin):
    """
    Admin interface for projects events.
    
    Because there are many events the list display is kept
    simple and uses related ids rather than selecting replated objects.
    """

    list_display = ["id", "time", "project_id", "user_id", "source_id"]


@admin.register(Source)
class SourceParentAdmin(PolymorphicParentModelAdmin):
    """Base admin class for source classes."""

    base_model = Source
    child_models = (
        ElifeSource,
        GithubSource,
        GoogleDocsSource,
        UploadSource,
        UrlSource,
    )

    list_display = [
        "id",
        "project_id",
        "path",
        "creator_id",
        "created",
        "updated",
        "polymorphic_ctype",
    ]
    list_select_related = ["polymorphic_ctype"]
    list_filter = [PolymorphicChildModelFilter]
    show_full_result_count = False


class SourceChildAdmin(PolymorphicChildModelAdmin):
    """Base admin class for all child models of Source."""


@admin.register(ElifeSource)
class ElifeSourceAdmin(SourceChildAdmin):
    """Admin interface for eLife sources."""

    base_model = ElifeSource
    show_in_index = True


@admin.register(GithubSource)
class GithubSourceAdmin(SourceChildAdmin):
    """Admin interface for GitHub sources."""

    base_model = GithubSource
    show_in_index = True


@admin.register(GoogleDocsSource)
class GoogleDocsSourceAdmin(SourceChildAdmin):
    """Admin interface for GoogleDocs sources."""

    base_model = GoogleDocsSource
    show_in_index = True


@admin.register(UploadSource)
class UploadSourceAdmin(SourceChildAdmin):
    """Admin interface for upload sources."""

    base_model = UploadSource
    show_in_index = True


@admin.register(UrlSource)
class UrlSourceAdmin(SourceChildAdmin):
    """Admin interface for URL sources."""

    base_model = UrlSource
    show_in_index = True


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    """Admin interface for project files."""

    list_display = [
        "id",
        "project",
        "path",
        "current",
        "created",
        "updated",
        "mimetype",
        "size",
    ]
    list_select_related = ["project"]
    list_filter = ["project"]


@admin.register(Snapshot)
class SnapshotAdmin(admin.ModelAdmin):
    """Admin interface for project snapshots."""

    list_display = ["id", "project", "number", "creator", "created"]
    list_select_related = ["project", "creator", "job"]


@admin.register(Node)
class NodeAdmin(admin.ModelAdmin):
    """Admin interface for project nodes."""

    list_display = ["id", "key", "creator", "created", "project", "app", "host"]
    list_select_related = ["creator", "project"]
    list_filter = ["app"]
    show_full_result_count = False

    def get_queryset(self, request):
        """Get custom queryset that does not fetch the `json` field (which can be large)."""
        queryset = super().get_queryset(request)
        return queryset.defer("json")
