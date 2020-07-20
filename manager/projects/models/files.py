import os
from datetime import datetime
from typing import Dict, Optional

from django.db import models
from django.shortcuts import reverse
from django.utils import timezone

from jobs.models import Job
from manager.storage import snapshots_storage, working_storage
from projects.models.projects import Project
from projects.models.sources import Source

SNAPSHOTS_STORAGE = snapshots_storage()
WORKING_STORAGE = working_storage()


class File(models.Model):
    """
    A file associated with a project.

    Files may be derived from a source, or from another file.
    """

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="files",
        null=False,
        blank=False,
        help_text="The project that the file is associated with.",
    )

    job = models.ForeignKey(
        Job,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="files",
        help_text="The job that created the file e.g. a source pull or file conversion.",
    )

    source = models.ForeignKey(
        Source,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="files",
        help_text="The source from which the file came (if any). "
        "If the source is removed from the project, so will the files.",
    )

    snapshot = models.ForeignKey(
        "Snapshot",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="files",
        help_text="The snapshot that the file belongs. "
        "If the snapshot is deleted so will the files.",
    )

    dependencies = models.ManyToManyField(
        "File",
        related_name="dependants",
        help_text="Files that this file was derived from.",
    )

    path = models.TextField(
        null=False,
        blank=False,
        db_index=True,
        help_text="The path of the file within the project.",
    )

    created = models.DateTimeField(
        auto_now_add=True, help_text="The time the file info was created."
    )

    updated = models.DateTimeField(
        auto_now=True, help_text="The time the file info was update."
    )

    modified = models.DateTimeField(
        null=True, blank=True, help_text="The file modification time."
    )

    size = models.PositiveIntegerField(
        null=True, blank=True, help_text="The size of the file in bytes",
    )

    mimetype = models.CharField(
        max_length=512, null=True, blank=True, help_text="The mimetype of the file.",
    )

    encoding = models.CharField(
        max_length=512,
        null=True,
        blank=True,
        help_text="The encoding of the file e.g. gzip",
    )

    @staticmethod
    def create(
        project: Project, path: str, info: Dict, job=None, source=None, snapshot=None
    ):
        """
        Create a file from info dictionary.

        Jobs return a dictionary of file information for each
        file that has been updated. This creates a `File` instance based
        on that informaton.
        
        Uses `get_or_create` to avoid duplicate entries e.g. if a
        job callback is accidentally called twice.
        """
        return File.objects.get_or_create(
            project=project,
            job=job,
            source=source,
            snapshot=snapshot,
            path=path,
            modified=get_modified(info),
            size=info.get("size"),
            mimetype=info.get("mimetype"),
            encoding=info.get("encoding"),
        )

    def update(self, info: Dict, job=None, source=None):
        """
        Update the file with info dictionary.
        """
        modified = info.get("modified")
        self.modified = get_modified(info)
        self.size = info.get("size")
        self.mimetype = info.get("mimetype")
        self.encoding = info.get("encoding")
        self.job = job
        self.source = source
        self.save()

    def open_url(self) -> Optional[str]:
        """
        Get a URL to open the file at the source.

        Currently, simply returns the URL to "open" the `source` (if any).
        In the future, each source type should provide a URL to edit a
        particular file from a multi-file source (e.g. a file within a Github repo).

        Does not provide the URL of the source directly because that would
        require additional queries to the table for each source type (instead provides URL
        to API endpoint which will redirect to the URL).

        Intentionally returns `None` for files in a snapshot (they do not have a `source`).
        """
        return (
            reverse(
                "api-projects-sources-open",
                kwargs=dict(project=self.project_id, source=self.source_id),
            )
            if self.source_id
            else None
        )

    def download_url(self) -> str:
        """
        Get a URL to download the file.

        The link will vary depending upon if the file is in the project's
        working directory, or if it is in a project snapshot.
        """
        if self.snapshot:
            return SNAPSHOTS_STORAGE.url(
                os.path.join(str(self.project.id), str(self.snapshot.id), self.path)
            )
        else:
            return WORKING_STORAGE.url(os.path.join(str(self.project.id), self.path))


def get_modified(info: Dict) -> Optional[datetime]:
    """
    Get the modified data as a timezone aware datetime object.
    """
    timestamp = info.get("modified")
    return datetime.fromtimestamp(timestamp, tz=timezone.utc) if timestamp else None
