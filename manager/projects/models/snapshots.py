import os

from django.db import models

from jobs.models import Job, JobMethod
from manager.storage import snapshots_storage
from projects.models.files import File
from projects.models.projects import Project
from users.models import User

storage = snapshots_storage()


class Snapshot(models.Model):
    """
    A project snapshot.
    """

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="snapshots",
        null=False,
        blank=False,
        help_text="The project that the snapshot is for.",
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

    job = models.ForeignKey(
        Job,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="The job that created the snapshot",
    )

    @staticmethod
    def create(project: Project, user: User) -> Job:
        """
        Snapshot the project.

        Pulls the project and creates a copy of its working
        directory.
        """
        snapshot = Snapshot.objects.create(project=project, creator=user)

        # Job to pull the project
        pull_subjob = project.pull(user)

        # Job to create an index.html
        options = {}

        main = project.get_main()
        if main.mimetype:
            options["from"] = main.mimetype

        theme = project.get_theme()
        if theme:
            options["theme"] = theme

        # TODO: If no main file then generate a file listing index.
        index_subjob = Job.objects.create(
            method=JobMethod.convert.name,
            params=dict(
                project=project.id,
                input=main.path,
                output="index.html",
                options=options,
            ),
            description="Create index.html",
            project=project,
            creator=user,
        )

        # Job to copy working directory to snapshot directory
        copy_subjob = Job.objects.create(
            method=JobMethod.copy.name,
            params=dict(project=project.id, snapshot=snapshot.id),
            description="Copy project '{0}'".format(project.name),
            project=project,
            creator=user,
            **Job.create_callback(snapshot, "copy_callback")
        )

        job = Job.objects.create(
            method=JobMethod.series.name,
            description="Snapshot project '{0}'".format(project.name),
            project=project,
            creator=user,
        )
        job.children.set([pull_subjob, index_subjob, copy_subjob])
        job.dispatch()

        snapshot.job = job
        snapshot.save()

        return snapshot

    def copy_callback(self, job: Job):
        """
        Update the files associated with this snapshot.

        Called when the snapshot's job final `copy` sub-job is complete.
        """
        result = job.result
        if not result:
            return

        for path, info in result.items():
            File.create(self.project, path, info, job=job, snapshot=self)

    @property
    def is_active(self) -> bool:
        """
        Is the snapshot currently active.
        """
        return self.job and self.job.is_active

    def archive_url(self, format: str = "zip") -> str:
        """
        Get the URL for a snapshot archive.
        """
        return storage.url(
            os.path.join(str(self.project.id), str(self.id) + "." + format)
        )
