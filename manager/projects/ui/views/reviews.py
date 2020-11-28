from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from projects.api.serializers import ReviewUpdateSerializer
from projects.api.views.reviews import ProjectsReviewsViewSet


def list(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """
    List reviews for a project.
    """
    viewset = ProjectsReviewsViewSet.init("list", request, args, kwargs)
    reviews = viewset.get_queryset()
    context = viewset.get_response_context(queryset=reviews)
    meta = viewset.get_project().get_meta()
    return render(request, "projects/reviews/list.html", dict(**context, meta=meta))


def create(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """
    Create a review for a project.
    """
    viewset = ProjectsReviewsViewSet.init("create", request, args, kwargs)
    serializer = viewset.get_serializer()
    context = viewset.get_response_context(serializer=serializer)
    meta = viewset.get_project().get_meta()
    return render(request, "projects/reviews/create.html", dict(**context, meta=meta))


def retrieve(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """
    Retrieve a review from a project.
    """
    viewset = ProjectsReviewsViewSet.init("retrieve", request, args, kwargs)
    review = viewset.get_object()
    context = viewset.get_response_context(instance=review)
    serializer = (
        ReviewUpdateSerializer()
        if context.get("is_editor") or context.get("is_user")
        else None
    )
    meta = viewset.get_project().get_meta()
    return render(
        request,
        "projects/reviews/retrieve.html",
        dict(**context, serializer=serializer, meta=meta),
    )
