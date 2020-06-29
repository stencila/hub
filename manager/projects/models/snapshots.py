from django.db import models

from jobs.models import Job, JobMethod
from projects.models.projects import Project
from users.models import User


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
        on_delete=models.PROTECT,
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

        job = Job.objects.create(
            method=JobMethod.series.name,
            description="Snapshot project '{0}'".format(project.name),
            project=project,
            creator=user,
        )
        job.children.set(
            [
                project.pull(user),
                Job.objects.create(
                    method=JobMethod.copy.name,
                    params=dict(project=project.id, snapshot=snapshot.id),
                    description="Copy project '{0}'".format(project.name),
                    project=project,
                    creator=user,
                ),
            ]
        )
        job.dispatch()

        snapshot.job = job
        snapshot.save()

        return snapshot
