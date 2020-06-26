from datetime import datetime
from typing import Dict

from django.db import models

from jobs.models import Job
from projects.models.projects import Project


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
        "Source",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="files",
        help_text="The source from which the file came (if any). "
        "If the source is removed from the project, so will the files.",
    )

    dependencies = models.ManyToManyField(
        "File",
        related_name="dependants",
        help_text="Files that this file was derived from.",
    )

    path = models.TextField(
        null=False, blank=False, help_text="The path of the file within the project.",
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
        project: Project, path: str, info: Dict, job=None, source=None,
    ):
        """
        Create a file from info dictionary.
        """
        modified = info.get("modified")
        return File.objects.create(
            project=project,
            job=job,
            source=source,
            path=path,
            modified=datetime.fromtimestamp(modified) if modified else None,
            size=info.get("size"),
            mimetype=info.get("mimetype"),
            encoding=info.get("encoding"),
        )

    def update(self, info: Dict, job=None, source=None):
        """
        Update the file with info dictionary.
        """
        modified = info.get("modified")
        self.modified = datetime.fromtimestamp(modified) if modified else None
        self.size = info.get("size")
        self.mimetype = info.get("mimetype")
        self.encoding = info.get("encoding")
        self.job = job
        self.source = source
        self.save()
