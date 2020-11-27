from typing import Optional

from django.shortcuts import reverse
from rest_framework import exceptions, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from manager.api.helpers import HtmxCreateMixin, HtmxListMixin, HtmxRetrieveMixin
from projects.api.serializers import ReviewCreateSerializer, ReviewRetrieveSerializer
from projects.api.views.projects import get_project
from projects.models.projects import Project, ProjectRole
from projects.models.reviews import Review, ReviewStatus


class ProjectsReviewsViewSet(
    HtmxListMixin, HtmxCreateMixin, HtmxRetrieveMixin, viewsets.GenericViewSet,
):
    """A view set for project reviews."""

    lookup_url_kwarg = "review"
    object_name = "review"
    queryset_name = "reviews"

    def get_permissions(self):
        """
        Get the permissions that the current action requires.

        Override defaults so that `list` and `retrieve` do not require
        authentication (although get_project() may deny access if not a public project).
        """
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_project(self) -> Project:
        """
        Get the project, checking that user has necessary role for the current action.

        Allow everyone to list and retrieve reviews.
        Only allows editors and above to create review objects.
        """
        if not hasattr(self, "project"):
            self.project = get_project(
                self.kwargs,
                self.request.user,
                [
                    ProjectRole.EDITOR,
                    ProjectRole.AUTHOR,
                    ProjectRole.MANAGER,
                    ProjectRole.OWNER,
                ]
                if self.action in ["create", "cancel", "extract"]
                else None,
            )
        return self.project

    def get_queryset(self, project: Optional[Project] = None):
        """
        Get all the reviews for the project.
        """
        return (
            Review.objects.filter(project=project or self.get_project())
            .order_by("-created")
            .select_related("creator", "creator__personal_account")
        )

    def get_object(self, project: Optional[Project] = None) -> Review:
        """
        Get a single review for the project.
        """
        try:
            return (
                self.get_queryset(project)
                .select_related("project__account")
                .get(id=self.kwargs["review"])
            )
        except Review.DoesNotExist:
            raise exceptions.NotFound

    def get_serializer_class(self):
        """
        Get the serializer class for the current action.

        Checks that the user is able to create a review for the project.
        """
        if self.action == "create" and not getattr(self, "swagger_fake_view", False):
            self.get_project()
            return ReviewCreateSerializer
        return ReviewRetrieveSerializer

    def get_success_url(self, serializer):
        """
        Get the URL to use in the Location header when an action is successful.

        For `create`, redirects to the page for the review.
        """
        if self.action in ["create"]:
            project = self.get_project()
            review = serializer.instance
            return reverse(
                "ui-projects-reviews-retrieve",
                args=[project.account.name, project.name, review.id],
            )

    def get_response_context(self, *args, **kwargs):
        """
        Get the context for rendering templates for this view set.
        """
        project = self.get_project()
        return super().get_response_context(
            *args, **kwargs, account=project.account, project=project
        )

    @action(detail=True, methods=["post"])
    def cancel(self, request: Request, *args, **kwargs) -> Response:
        """
        Cancel the review invite (if any).
        """
        review = self.get_object()
        if review.status != ReviewStatus.INVITED.name or not review.invite:
            raise exceptions.NotAcceptable()
        review.status = ReviewStatus.CANCELLED.name
        review.save()
        review.invite.delete()
        return Response()

    @action(detail=True, methods=["post"])
    def extract(self, request: Request, *args, **kwargs) -> Response:
        """
        Extract the review from its source.

        Creates and dispatches an `extract` job on the review's source.
        """
        review = self.get_object()
        review.job = review.source.extract(
            review=review, user=request.user, filters=dict(name=review.reviewer_name)
        )
        review.job.dispatch()
        review.status = ReviewStatus.EXTRACTING.name
        review.save()
        return Response()
