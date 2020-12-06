import logging
import re
import time
from datetime import datetime
from typing import Optional

from django.conf import settings
from django.db import models
from django.dispatch import receiver
from django.utils import timezone

from jobs.models import Job, JobMethod
from manager.signals import email_received
from projects.models.nodes import Node
from users.models import User

logger = logging.getLogger(__name__)


class Doi(models.Model):
    """
    A Digital Object Identifier (DOI).

    All Stencila DOIs point to a CreativeWork node of some type e.g. Article, Review, Dataset.
    The node is the source of bibliographic metadata used when registering the DOI.
    The node is protected from deletion.

    We use a common base URL for the registered DOI URLs and then redirect from that URL
    to the node. This enables changes over time in the URL for the node, without breaking
    the permanent, registered DOI URL. We store the DOI URL as a record e.g in case there
    are changes in the base URL convention.
    """

    doi = models.CharField(
        max_length=128,
        help_text="The DOI string including both prefix and suffix e.g. 10.47704/stencila.54321",
    )

    url = models.URLField(
        help_text="The URL registered for the DOI. e.g. https://hub.stenci.la/doi/10.47704/stencila.54321",
    )

    node = models.ForeignKey(
        Node,
        on_delete=models.PROTECT,
        related_name="dois",
        help_text="The Stencila node that the DOI points to.",
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

    job = models.ForeignKey(
        Job,
        on_delete=models.SET_NULL,
        related_name="doi_registered",
        null=True,
        blank=True,
        help_text="The job that registered the DOI.",
    )

    deposited = models.DateField(
        null=True,
        blank=True,
        help_text="Date-time that the deposit request was sent to the registrar.",
    )

    deposit_request = models.JSONField(
        null=True,
        blank=True,
        help_text="JSON serialization of the deposit request sent to the registrar.",
    )

    deposit_response = models.JSONField(
        null=True,
        blank=True,
        help_text="JSON serialization of the deposit response received from the registrar.",
    )

    deposit_success = models.BooleanField(
        null=True, blank=True, help_text="Whether or not the deposit was successful.",
    )

    registered = models.DateField(
        null=True,
        blank=True,
        help_text="Date-time that a registration notification was received from the registrar.",
    )

    registration_response = models.JSONField(
        null=True,
        blank=True,
        help_text="The payload received from the registrar on notification.",
    )

    registration_success = models.BooleanField(
        null=True,
        blank=True,
        help_text="Whether or not the registration was successful.",
    )

    def save(self, *args, **kwargs):
        """
        Override save to ensure that `doid` and `url` attributes are set based on the `id`.
        """
        super().save(*args, **kwargs)

        if not self.doi:
            self.doi = f"{settings.DOI_PREFIX}/{settings.DOI_SUFFIX_LEFT}{self.id}"
            self.url = f"http{'' if settings.DEBUG else 's'}://{settings.PRIMARY_DOMAIN}/doi/{self.doi}"
            self.save()

    def get_progress(self) -> int:
        """
        Get a number describing progress of the DOI registration.

        0 = not deposited yet
        1 = deposit failed
        2 = deposit succeeded
        3 = registration failed
        4 = registration succeeded
        """
        if self.registration_success:
            return 4
        if self.registered:
            return 3
        if self.deposit_success:
            return 2
        if self.deposited:
            return 1
        return 0

    def register(self, user: Optional[User] = None) -> Job:
        """
        Register the DOI.

        Creates a job that asynchronously registers the DOI with a
        registration agency.
        """
        job = Job.objects.create(
            description="Register DOI",
            method=JobMethod.register.name,
            params=dict(
                node=self.node.json,
                doi=self.doi,
                url=self.url,
                batch=f"{self.id}@{time.time()}",
            ),
            project=self.node and self.node.project,
            creator=user,
            **Job.create_callback(self, "register_callback"),
        )
        self.job = job
        self.save()
        return job

    def register_callback(self, job: Job):
        """
        Store registration details resulting from a `register` job.
        """
        result = job.result
        if result:

            def get_date(name):
                return (
                    datetime.fromisoformat(result.get(name).replace("Z", "+00:00"))
                    if result.get(name)
                    else None
                )

            success = result.get("deposit_success")

            self.deposited = get_date("deposited")
            self.deposit_request = result.get("deposit_request")
            self.deposit_response = result.get("deposit_response")
            self.deposit_success = success
            self.save()

            if not success:
                logger.error("Error depositing DOI", extra={"id": self.id})


@receiver(email_received)
def receive_registration_email(sender, email, **kwargs):
    """
    Record the registration confirmation (or rejection) email from Crossref.
    """
    if "@crossref.org" in email.get("from"):
        text = email.get("text")
        match = re.search(r"<batch_id>([^@]+)@", text)
        if match:
            success = '<record_diagnostic status="Success">' in text

            doi = Doi.objects.get(id=match.group(1))
            doi.registered = timezone.now()
            doi.registration_response = text
            doi.registration_success = success
            doi.save()

            if not success:
                logger.error("Error registering DOI", extra={"text": text})
        else:
            logger.warning("Unable to find batch id", extra={"text": text})
