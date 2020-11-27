from datetime import datetime
from typing import List, Optional, Tuple

from django.db import models

from jobs.models import Job
from manager.helpers import EnumChoice
from projects.models.nodes import Node
from projects.models.projects import Project
from projects.models.sources import Source
from users.models import Invite, User


class ReviewStatus(EnumChoice):
    """
    The status of a review.
    """

    PENDING = "PENDING"
    INVITED = "INVITED"
    ACCEPTED = "ACCEPTED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"
    EXTRACTING = "EXTRACTING"
    EXTRACTED = "EXTRACTED"
    FAILED = "FAILED"

    @staticmethod
    def as_choices() -> List[Tuple[str, str]]:
        """Return as a list of field choices."""
        return [
            (ReviewStatus.PENDING.name, "Pending"),
            (ReviewStatus.INVITED.name, "Invited"),
            (ReviewStatus.ACCEPTED.name, "Accepted"),
            (ReviewStatus.CANCELLED.name, "Cancelled"),
            (ReviewStatus.COMPLETED.name, "Completed"),
            (ReviewStatus.EXTRACTING.name, "Retrieval in progress"),
            (ReviewStatus.EXTRACTED.name, "Retrieved"),
            (ReviewStatus.FAILED.name, "Retrieval failed"),
        ]

    @classmethod
    def get_description(cls, status: str) -> Optional[str]:
        """Return the description of the status."""
        choices = cls.as_choices()
        for choice in choices:
            if status == choice[0]:
                return choice[1]
        return None


class Review(models.Model):
    """
    A review of a `Node` within a project.

    The `subject` of the review will usually be an `Article`, or other type
    of `CreativeWork` node, generated from a snapshot.
    """

    project = models.ForeignKey(
        Project,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name="reviews",
        help_text="The project that the review is for.",
    )

    creator = models.ForeignKey(
        User,
        # Usually set but allow for null if user is deleted
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="reviews_created",
        help_text="The user who created the review.",
    )

    created = models.DateTimeField(
        auto_now_add=True, help_text="The time the review was created."
    )

    updated = models.DateTimeField(
        auto_now=True, help_text="The time the review was last updated."
    )

    status = models.CharField(
        max_length=16,
        choices=ReviewStatus.as_choices(),
        default=ReviewStatus.PENDING.name,
        help_text="The status of the review.",
    )

    source = models.ForeignKey(
        Source,
        # Should normally be set but allow for
        # null if the the source is removed from the project
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="reviews",
        help_text="The source for this review.",
    )

    reviewer = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="reviews_authored",
        help_text="The user who authored the review.",
    )

    reviewer_email = models.EmailField(
        null=True, blank=True, help_text="The email address of the reviewer.",
    )

    reviewer_name = models.CharField(
        max_length=128, null=True, blank=True, help_text="The name of the reviewer.",
    )

    invite_message = models.TextField(
        null=True,
        blank=True,
        help_text="The message to send to the reviewer in the invitation.",
    )

    invite = models.ForeignKey(
        Invite,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="The invite sent to the reviewer.",
    )

    job = models.ForeignKey(
        Job,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="reviews",
        help_text="The job that extracted the review from the source.",
    )

    subject = models.ForeignKey(
        Node,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="reviews",
        help_text="The node, usually a `CreativeWork`, that is the subject of the review.",
    )

    review = models.ForeignKey(
        Node,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        help_text="The node, of type `Review`, representing the actual review.",
    )

    # The following fields are derived from the `review.json` when a `Review` model
    # is extracted from a source. They are mostly optimizations to avoid fetching the
    # JSON of the review everytime we want to display them (e.g. in listings)

    review_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="The date of the review e.g it's `datePublished`.",
    )

    review_comments = models.IntegerField(
        null=True, blank=True, help_text="The number of comments that the review has."
    )

    def extract_callback(self, job: Job):
        """
        Store the extracted review.
        """
        json = job.result
        if not json:
            self.status = ReviewStatus.FAILED.name
        else:
            self.review = Node.objects.create(json=json)
            self.review_date = (
                json.get("datePublished")
                or json.get("dateModified")
                or json.get("dateCreated")
            )
            self.review_comments = len(json.get("comments", []))
            self.status = ReviewStatus.EXTRACTED.name
        self.save()

    # The following methods get derived properties of the review for use in templates
    # or API responses

    def get_status(self) -> Optional[str]:
        """
        Get a human readable string describing the status of the review.
        """
        return ReviewStatus.get_description(self.status)

    def get_date(self) -> datetime:
        """
        Get the date for the review.

        Returns the declared review date or when the review was last updated.
        """
        return self.review_date or self.updated or self.created()

    def get_reviewer_name(self) -> Optional[str]:
        """
        Get the name for the reviewer.

        Returns the account display name for reviewers that are users.
        Returns the `reviewer_name` (which may be null) otherwise.
        """
        return (
            self.reviewer.personal_account.display_name or self.reviewer.username
            if self.reviewer
            else self.reviewer_name
        )

    def get_reviewer_image(self) -> Optional[str]:
        """
        Get the image for the reviewer.

        Returns the account image for reviewers that are users.
        Returns null otherwise.
        """
        return self.reviewer.personal_account.image.medium if self.reviewer else None

    def get_doi(self) -> Optional[str]:
        """
        Get the DOI of the review.

        It is possible for a `Node` to have multiple DOIs assigned to it, so
        we get the latest.
        """
        return self.review and self.review.dois.order_by("-created").first()

    def get_comments(self) -> Optional[int]:
        """
        Get the number of comments that the review has.
        """
        return self.review_comments
