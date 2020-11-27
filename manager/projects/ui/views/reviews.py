from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from projects.api.views.reviews import ProjectsReviewsViewSet


def list(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """
    List reviews for a project.
    """
    viewset = ProjectsReviewsViewSet.init("list", request, args, kwargs)
    context = viewset.get_response_context()
    reviews = viewset.get_queryset()
    meta = viewset.get_project().get_meta()
    return render(
        request,
        "projects/reviews/list.html",
        dict(**context, reviews=reviews, meta=meta),
    )


def create(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """
    Create a review for a project.
    """
    viewset = ProjectsReviewsViewSet.init("create", request, args, kwargs)
    context = viewset.get_response_context()
    serializer = viewset.get_serializer()
    meta = viewset.get_project().get_meta()
    return render(
        request,
        "projects/reviews/create.html",
        dict(**context, serializer=serializer, meta=meta),
    )


def retrieve(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """
    Retrieve a review from a project.
    """
    viewset = ProjectsReviewsViewSet.init("retrieve", request, args, kwargs)
    context = viewset.get_response_context()
    review = viewset.get_object()
    meta = viewset.get_project().get_meta()
    return render(
        request,
        "projects/reviews/retrieve.html",
        dict(**context, review=review, meta=meta),
    )
