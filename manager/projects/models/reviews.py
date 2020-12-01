import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import shortuuid
from django.db import models

from jobs.models import Job
from manager.helpers import EnumChoice
from projects.models.nodes import Node
from projects.models.projects import Project, ProjectAgent, ProjectRole
from projects.models.sources import Source
from users.models import User


class ReviewStatus(EnumChoice):
    """
    The status of a review.
    """

    PENDING = "PENDING"
    REQUESTED = "REQUESTED"
    CANCELLED = "CANCELLED"
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"
    COMPLETED = "COMPLETED"
    EXTRACTING = "EXTRACTING"
    EXTRACTED = "EXTRACTED"
    FAILED = "FAILED"

    @staticmethod
    def as_choices() -> List[Tuple[str, str]]:
        """Return as a list of field choices."""
        return [
            (ReviewStatus.PENDING.name, "Pending"),
            (ReviewStatus.REQUESTED.name, "Requested"),
            (ReviewStatus.CANCELLED.name, "Cancelled"),
            (ReviewStatus.ACCEPTED.name, "Accepted"),
            (ReviewStatus.DECLINED.name, "Declined"),
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


def generate_review_key():
    """
    Generate a unique, and very difficult to guess, key for a review.
    """
    return shortuuid.ShortUUID().random(length=32)


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

    key = models.CharField(
        default=generate_review_key,
        max_length=64,
        help_text="A unique, and very difficult to guess, key for the reviewer "
        "to access the review if they are not a user.",
    )

    request_message = models.TextField(
        null=True,
        blank=True,
        help_text="The message sent to the reviewer in the request to review.",
    )

    response_message = models.TextField(
        null=True,
        blank=True,
        help_text="The message provided by the reviewer when accepting or declining to review.",
    )

    cancel_message = models.TextField(
        null=True,
        blank=True,
        help_text="The message sent to the reviewer when the review was cancelled.",
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

    review_author_name = models.CharField(
        max_length=128, null=True, blank=True, help_text="The name of the reviewer.",
    )

    review_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="The date of the review e.g it's `datePublished`.",
    )

    review_comments = models.IntegerField(
        null=True, blank=True, help_text="The number of comments that the review has."
    )

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
        Returns the `review_author_name` (which may be null) otherwise.
        """
        return (
            self.reviewer.personal_account.display_name or self.reviewer.username
            if self.reviewer
            else self.review_author_name
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

    # Actions on a review

    def request(self):
        """
        Send the request to the reviewer.
        """
        if self.reviewer_email or self.reviewer:
            # TODO Send the email
            # email = self.reviewer_email or get_email(self.reviewer)
            # invite = Invite.objects.create(
            #    inviter=creator,
            #    email=email,
            #    message=self.invite_message,
            #    action=InviteAction.make_self.name,
            #    subject_type=ContentType.objects.get_for_model(Review),
            #    subject_id=self.id,
            #    arguments=dict(
            #        account=self.project.account.id,
            #        project=self.project.id,
            #        review=self.id,
            #    ),
            # )
            # invite.send_invitation(request)

            self.status = ReviewStatus.REQUESTED.name
            self.save()

    def update(
        self,
        status: str,
        response_message: Optional[str] = None,
        cancel_message: Optional[str] = None,
        user: Optional[User] = None,
        filters: Dict = {},
    ):
        """
        Update the status of a review.

        Checks that the status update makes logical sense and
        records the message and user (if any). Note that a status
        update to `ACCEPTED`, `DECLINED` or `COMPLETED` can be made
        by an anonymous users (a reviewer who has the review key but
        is not an authenticated user).
        """
        if (
            status == ReviewStatus.CANCELLED.name
            and self.status == ReviewStatus.REQUESTED.name
        ):
            self.cancel_message = cancel_message or None
        elif (
            status == ReviewStatus.ACCEPTED.name
            and self.status == ReviewStatus.REQUESTED.name
        ):
            self.reviewer = user
            self.response_message = response_message or None

            # Add user as a REVIEWER to the project (if necessary)
            try:
                agent = ProjectAgent.objects.get(project_id=self.project, user=user)
            except ProjectAgent.DoesNotExist:
                ProjectAgent.objects.create(
                    project_id=self.project, user=user, role=ProjectRole.REVIEWER.name,
                )
            else:
                if agent.role not in ProjectRole.and_above(ProjectRole.REVIEWER):
                    agent.role = ProjectRole.REVIEWER.name
                    agent.save()
        elif (
            status == ReviewStatus.DECLINED.name
            and self.status == ReviewStatus.REQUESTED.name
        ):
            self.reviewer = user
            self.response_message = response_message or None
        elif status == ReviewStatus.COMPLETED.name and self.status in (
            ReviewStatus.PENDING.name,
            ReviewStatus.ACCEPTED.name,
            ReviewStatus.FAILED.name,
        ):
            self.extract(user, filters)
        else:
            raise ValueError(
                f"Review can not be updated from {self.status} to {status}."
            )

        self.status = status
        self.save()

    def extract(self, user: User, filters: Dict = {}):
        """
        Extract the review from its source.

        Parses the filters according to the type of source.
        Creates and dispatches an `extract` job on the review's source.
        """
        if self.source.type_name == "Github":
            match = re.match(
                r"https:\/\/github.com\/(?:\w+)\/(?:\w+)\/pull\/(\d+)#pullrequestreview-(\d+)",
                filters.get("filter_a", ""),
            )
            if match:
                filters = dict(
                    pr_number=int(match.group(1)), review_id=int(match.group(2))
                )
        elif self.source.type_name.startswith("Google"):
            filters = dict(name=filters.get("filter_a"))

        job = self.source.extract(review=self, user=user, filters=filters)
        job.dispatch()

        self.job = job
        self.status = ReviewStatus.EXTRACTING.name
        self.save()

    def extract_callback(self, job: Job):
        """
        Store the extracted review.
        """
        json = job.result
        if not json:
            self.status = ReviewStatus.FAILED.name
        else:
            self.review = Node.objects.create(
                project=self.project, creator=job.creator, app="hub.reviews", json=json
            )
            authors = json.get("authors", [])
            if len(authors) > 0:
                self.review_author_name = authors[0].get("name")
            self.review_date = (
                json.get("datePublished")
                or json.get("dateModified")
                or json.get("dateCreated")
            )
            self.review_comments = len(json.get("comments", []))
            self.status = ReviewStatus.EXTRACTED.name
        self.save()
