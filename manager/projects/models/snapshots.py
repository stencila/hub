import os
from typing import Optional

import shortuuid
from django.db import models
from django.http import HttpRequest
from django.utils import timezone

from jobs.models import Job, JobMethod
from manager.storage import StorageUsageMixin, snapshots_storage
from projects.models.files import File, get_modified
from projects.models.projects import Project
from users.models import User


def generate_snapshot_id():
    """
    Generate a unique snapshot id.

    The is separate function to avoid new AlterField migrations
    being created as happens when `default=shortuuid.uuid`.
    """
    return shortuuid.uuid()


class Snapshot(StorageUsageMixin, models.Model):
    """
    A project snapshot.

    The `path` field is stored on the model to improve durability (if
    the convention for creating paths changes, the existing paths will not change).

    The `zip_name` field provides a way of providing a more useful filename
    when downloading the archive (it is populated with the project name and snapshot number).
    """

    id = models.CharField(
        primary_key=True,
        max_length=32,
        editable=False,
        default=generate_snapshot_id,
        help_text="The unique id of the snapshot.",
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="snapshots",
        null=False,
        blank=False,
        help_text="The project that the snapshot is for.",
    )

    number = models.IntegerField(
        db_index=True, help_text="The number of the snapshot within the project.",
    )

    creator = models.ForeignKey(
        User,
        null=True,
        on_delete=models.SET_NULL,
        related_name="snapshots_created",
        help_text="The user who created the snapshot.",
    )

    created = models.DateTimeField(
        auto_now_add=True, help_text="The time the snapshot was created."
    )

    path = models.CharField(
        max_length=1024,
        null=True,
        help_text="The path of the snapshot's directory within the snapshot storage volume.",
    )

    zip_name = models.CharField(
        max_length=1024,
        null=True,
        help_text="The name of snapshot's Zip file (within the snapshot directory).",
    )

    container_image = models.TextField(
        null=True,
        blank=True,
        help_text="The container image to use as the execution environment for this snapshot.",
    )

    job = models.ForeignKey(
        Job,
        on_delete=models.SET_NULL,
        related_name="snapshot_created",
        null=True,
        blank=True,
        help_text="The job that created the snapshot",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["project", "number"], name="%(class)s_unique_project_number"
            )
        ]

    STORAGE = snapshots_storage()

    def __str__(self):
        """
        Get a string representation to use in select options etc.
        """
        return "Snapshot #{0}".format(self.number)

    def save(self, *args, **kwargs):
        """
        Override to ensure certain fields are populated.

        Ensures that:

        - `number` is not null and monotonically increases
        - `path` and `zip_name` are set
        """
        if self.number is None:
            result = Snapshot.objects.filter(project=self.project).aggregate(
                models.Max("number")
            )
            self.number = (result["number__max"] or 0) + 1

        if not self.path:
            self.path = os.path.join(str(self.project.id), str(self.id))

        if not self.zip_name:
            self.zip_name = "{project}-v{number}.zip".format(
                project=self.project.name, number=self.number
            )

        return super().save(*args, **kwargs)

    @staticmethod
    def create(project: Project, user: User) -> Job:
        """
        Snapshot the project.
        """
        snapshot = Snapshot.objects.create(project=project, creator=user)

        subjobs = []

        # Clean the project's working directory
        subjobs.append(project.cleanup(user))

        # Pull the project's sources
        subjobs.append(project.pull(user))

        # "Reflow" the project (regenerate derived files)
        # NB 2021-06-16 This is commented out because it was causing
        # many recursive jobs to be spawned (related to index.html ?)
        # Needs more testing, and possibly a different approach before
        # reintroducing.
        # reflow = project.reflow(user)
        # if reflow:
        #     subjobs.append(reflow)

        # Pin the container image
        subjobs.append(
            project.pin(user, **Job.create_callback(snapshot, "pin_callback"))
        )

        # Create an index.html if a "main" file is defined
        main = project.get_main()
        if main:
            options = {}

            theme = project.get_theme()
            if theme:
                options["theme"] = theme

            subjobs.append(main.convert(user, "index.html", options=options))

        # This is currently required to populate field `zip_name` below
        snapshot.save()

        # Archive the working directory to the snapshot directory
        subjobs.append(
            project.archive(
                user,
                snapshot=snapshot.id,
                path=f"{project.id}/{snapshot.id}/{snapshot.zip_name}",
                **Job.create_callback(snapshot, "archive_callback"),
            )
        )

        job = Job.objects.create(
            method=JobMethod.series.name,
            description="Snapshot project '{0}'".format(project.name),
            project=project,
            creator=user,
        )
        job.children.set(subjobs)
        job.dispatch()

        snapshot.job = job
        snapshot.save()

        return snapshot

    def pin_callback(self, job: Job):
        """
        Update the container image for this snapshot.

        Called when the `pin` sub-job is complete.
        """
        self.container_image = job.result
        self.save()

    def archive_callback(self, job: Job):
        """
        Update the files associated with this snapshot.

        Called when the `archive` sub-job is complete.
        """
        result = job.result
        if not result:
            return

        # Do a batch insert of files. This is much faster when there are a lot of file
        # than inserting each file individually.
        File.objects.bulk_create(
            [
                File(
                    project=self.project,
                    path=path,
                    current=False,
                    job=job,
                    snapshot=self,
                    updated=timezone.now(),
                    modified=get_modified(info),
                    size=info.get("size"),
                    mimetype=info.get("mimetype"),
                    encoding=info.get("encoding"),
                    fingerprint=info.get("fingerprint"),
                )
                for path, info in result.items()
            ]
        )

    def session(self, request: HttpRequest) -> Job:
        """
        Create a session job for the snapshot.
        """
        project = self.project
        job = Job.objects.create(
            project=project,
            creator=request.user if request.user.is_authenticated else None,
            snapshot=self,
            method=JobMethod.session.name,
            params=dict(
                snapshot=self.id,
                snapshot_url=self.file_url(self.zip_name),
                container_image=self.container_image,
                mem_request=project.session_memory,
                mem_limit=project.session_memory,
                timeout=project.session_timeout,
                timelimit=project.session_timelimit,
            ),
            description="Session for snapshot #{0}".format(self.number),
        )
        job.add_user(request)
        return job

    @property
    def is_active(self) -> bool:
        """
        Is the snapshot currently active.
        """
        return self.job and self.job.is_active

    @property
    def has_index(self) -> bool:
        """
        Determine if the snapshot has an index.html file, or not.
        """
        try:
            self.files.get(path="index.html")
            return True
        except File.DoesNotExist:
            return False

    def content_url(self, path: Optional[str] = None) -> str:
        """
        Get the URL that this snapshot content is served from.
        """
        return self.project.content_url(snapshot=self, path=path)

    def file_location(self, file: str) -> str:
        """
        Get the location of one of the snapshot's files relative to the root of the storage volume.
        """
        return os.path.join(self.path, file)
