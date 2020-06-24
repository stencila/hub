from django.db import models
from django.db.models.signals import post_save

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
        on_delete=models.DO_NOTHING,
        null=False,
        blank=False,
        help_text="The job that created the snapshot",
    )

    @staticmethod
    def create(project: Project, user: User) -> Job:
        """
        Snapshot the project.

        Creates a `parallel` job having children jobs that `pull`
        each source.
        """
        job = Job.objects.create(
            project=project, creator=user, method=JobMethod.parallel.name
        )
        job.children.set([source.pull(user) for source in project.sources.all()])
        job.dispatch()

        return Snapshot.objects.create(project=project, creator=user, job=job)
