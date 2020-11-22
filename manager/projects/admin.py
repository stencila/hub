from django.contrib import admin
from polymorphic.admin import (
    PolymorphicChildModelAdmin,
    PolymorphicChildModelFilter,
    PolymorphicParentModelAdmin,
)

from manager.admin import InputFilter, ProjectNameFilter, UserUsernameFilter
from projects.models.files import File
from projects.models.nodes import Node
from projects.models.projects import Project, ProjectAgent, ProjectEvent
from projects.models.providers import GithubRepo
from projects.models.snapshots import Snapshot
from projects.models.sources import (
    ElifeSource,
    GithubSource,
    GoogleDocsSource,
    GoogleDriveSource,
    GoogleSheetsSource,
    PlosSource,
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

    # If an admin class is not declared for each source type a 403
    # error is thrown when trying to edit that source in the admin interface.
    child_models = (
        ElifeSource,
        GithubSource,
        GoogleDocsSource,
        GoogleSheetsSource,
        GoogleDriveSource,
        PlosSource,
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


@admin.register(GoogleSheetsSource)
class GoogleSheetsSourceAdmin(SourceChildAdmin):
    """Admin interface for GoogleSheets sources."""

    base_model = GoogleSheetsSource
    show_in_index = True


@admin.register(GoogleDriveSource)
class GoogleDriveSourceAdmin(SourceChildAdmin):
    """Admin interface for GoogleDrive sources."""

    base_model = GoogleDriveSource
    show_in_index = True


@admin.register(PlosSource)
class PlosSourceAdmin(SourceChildAdmin):
    """Admin interface for PLOS sources."""

    base_model = PlosSource
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


class FilePathFilter(InputFilter):
    """
    Filter files by their path.
    """

    parameter_name = "path"
    title = "Path starts with"

    def queryset(self, request, queryset):
        """
        Filter the list of files by their path.
        """
        value = self.value()
        if value is not None:
            return queryset.filter(path__startswith=value)


class FileMimeTypeFilter(InputFilter):
    """
    Filter files by their MIME type.
    """

    parameter_name = "mimetype"
    title = "MIME type starts with"

    def queryset(self, request, queryset):
        """
        Filter the list of files by their MIME type.
        """
        value = self.value()
        if value is not None:
            return queryset.filter(mimetype__startswith=value)


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    """Admin interface for project files."""

    list_display = [
        "id",
        "project_full_name",
        "path",
        "current",
        "created",
        "updated",
        "mimetype",
        "size",
    ]
    list_select_related = ["project", "project__account"]
    list_filter = [
        ProjectNameFilter,
        FilePathFilter,
        FileMimeTypeFilter,
        "current",
        "created",
        "updated",
    ]

    def project_full_name(self, file):
        """Derive file's project full name."""
        return file.project and f"{file.project.account.name}/{file.project.name}"


@admin.register(Snapshot)
class SnapshotAdmin(admin.ModelAdmin):
    """Admin interface for project snapshots."""

    list_display = ["id", "project_full_name", "number", "created", "job_status"]
    list_select_related = ["project", "project__account", "job"]
    list_filter = [ProjectNameFilter, "created"]
    ordering = ["-created"]

    def project_full_name(self, snapshot):
        """Derive snapshot's project full name."""
        return (
            snapshot.project
            and f"{snapshot.project.account.name}/{snapshot.project.name}"
        )

    def job_status(self, snapshot):
        """Derive snapshot's job status."""
        return snapshot.job and snapshot.job.status


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


class GithubRepoFullnameFilter(InputFilter):
    """
    Filter repos by their full name.
    """

    parameter_name = "fullname"
    title = "Repo name contains"

    def queryset(self, request, queryset):
        """
        Filter the list of repos by similar names.
        """
        name = self.value()
        if name is not None:
            return queryset.filter(full_name__contains=name)


@admin.register(GithubRepo)
class GithubRepoAdmin(admin.ModelAdmin):
    """Admin interface for GitHub repos for a user."""

    list_display = ["id", "user", "full_name", "updated", "refreshed"]
    list_filter = [UserUsernameFilter, GithubRepoFullnameFilter, "refreshed", "updated"]
    show_full_result_count = False
