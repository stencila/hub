import datetime

from django.conf import settings
from django.db import models

from jobs.models import Job, JobMethod
from projects.models.nodes import Node
from users.models import User


class Doi(models.Model):
    """
    A Digital Object Identifier (DOI).
    """

    doi = models.CharField(
        max_length=128,
        help_text="The DOI string including both prefix and suffix e.g. 10.47704/stencila.54321",
    )

    url = models.URLField(
        help_text="The URL of the resource that this DOI is points to.",
    )

    node = models.ForeignKey(
        Node,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="dois",
        help_text="The node that the DOI points to. Most Stencila DOIs point to a CreativeWork node of some type "
        "e.g. a Article, a Review, a Dataset.",
    )

    creator = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="dois_created",
        help_text="The user who created the DOI.",
    )

    created = models.DateTimeField(
        auto_now_add=True, help_text="Date-time the DOI was created."
    )

    deposited = models.DateField(
        null=True,
        blank=True,
        help_text="Date-time that the registration request was sent to the registrar.",
    )

    registered = models.DateField(
        null=True,
        blank=True,
        help_text="Date-time that a successful registration response was received "
        "from the registrar. If `deposited` is not null and this is null it "
        "implies that the registration was unsuccessful.",
    )

    request = models.JSONField(
        null=True,
        blank=True,
        help_text="JSON serialization of the request sent to the registrar.",
    )

    response = models.JSONField(
        null=True,
        blank=True,
        help_text="JSON serialization of the response received from the registrar.",
    )

    def save(self, *args, **kwargs):
        """
        Override save to ensure that DOI attribute is set based on the id.
        """
        super().save(*args, **kwargs)

        if not self.doi:
            self.doi = f"{settings.DOI_PREFIX}/{settings.DOI_SUFFIX_LEFT}{self.id}"
            self.save()

    def register(self, user: User) -> Job:
        """
        Register the DOI.

        Creates a job which will asynchronously register the DOI when it is
        `dispatch()`ed.
        """
        return Job.objects.create(
            description="Register DOI",
            method=JobMethod.register.name,
            params=dict(doi=self.url, url=self.path, node=self.node),
            project=self.project,
            creator=user,
            **Job.create_callback(self, "register_callback"),
        )

    def register_callback(self, job: Job):
        """
        Store registration details resulting from a register job.
        """
        result = job.result
        if result:

            def get_date(name):
                return (
                    datetime.fromisoformat(result.get(name).replace("Z", "+00:00"))
                    if result.get(name)
                    else None
                )

            self.deposited = get_date("deposited")
            self.registered = get_date("registered")
            self.request = result.get("request")
            self.response = result.get("response")
            self.save()
