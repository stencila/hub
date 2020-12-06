from django.db.models import Q
from django.shortcuts import reverse
from rest_framework import exceptions, permissions, viewsets

from manager.api.helpers import (
    HtmxCreateMixin,
    HtmxListMixin,
    HtmxRetrieveMixin,
    HtmxUpdateMixin,
)
from projects.api.serializers import (
    ReviewCreateSerializer,
    ReviewRetrieveSerializer,
    ReviewUpdateSerializer,
)
from projects.api.views.projects import get_project
from projects.models.projects import Project, ProjectRole
from projects.models.reviews import Review, ReviewStatus


class ProjectsReviewsViewSet(
    HtmxListMixin,
    HtmxCreateMixin,
    HtmxRetrieveMixin,
    HtmxUpdateMixin,
    viewsets.GenericViewSet,
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
        Only allows EDITOR and above to create or update review objects.
        """
        if not hasattr(self, "project"):
            self.project = get_project(
                self.kwargs,
                self.request.user,
                ProjectRole.and_above(ProjectRole.EDITOR)
                if self.action in ["create", "partial_update", "extract"]
                else None,
            )
        return self.project

    def get_queryset(self):
        """
        Get a list of reviews for a project.

        Only list reviews that are EXTRACTED (ie. complete) unless the user is
        a project EDITOR or above.
        """
        project = self.get_project()
        return (
            Review.objects.filter(
                Q(status=ReviewStatus.EXTRACTED.name)
                if project.role
                not in [role.name for role in ProjectRole.and_above(ProjectRole.EDITOR)]
                else Q(),
                project=project,
            )
            .order_by("-created")
            .select_related("reviewer", "reviewer__personal_account", "review")
            .prefetch_related("review__dois")
        )

    def get_object(self) -> Review:
        """
        Get a single review for the project.
        """
        try:
            return (
                self.get_queryset()
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
        if self.action == "create":
            if not getattr(self, "swagger_fake_view", False):
                self.get_project()
            return ReviewCreateSerializer
        elif self.action == "partial_update":
            return ReviewUpdateSerializer
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
        instance = kwargs.get("instance")
        is_editor = (
            project.role
            in [role.name for role in ProjectRole.and_above(ProjectRole.EDITOR)]
            if instance
            else None
        )
        is_reviewer = (
            (
                self.request.user == instance.reviewer
                or self.request.GET.get("key") == instance.key
            )
            if instance
            else None
        )
        return super().get_response_context(
            *args,
            **kwargs,
            account=project.account,
            project=project,
            is_editor=is_editor,
            is_reviewer=is_reviewer
        )
