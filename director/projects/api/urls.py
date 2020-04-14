from django.urls import path, include
from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns

from projects.api.views.sources import (
    DiskItemCreateView,
    DiskItemMoveView,
    DiskItemRemoveView,
    SourceLinkView,
    ItemPublishView,
    PublishedItemDeleteView,
)
from projects.api.views.events import EventListView
from projects.api.views.nodes import NodesViewSet
from projects.api.views.projects import ProjectsViewSet
from projects.api.views.snapshots import SnapshotsViewSet

nodes = routers.SimpleRouter(trailing_slash=False)
nodes.register("", NodesViewSet, "api-nodes")
nodes_urls = format_suffix_patterns(nodes.urls)

projects = routers.SimpleRouter(trailing_slash=False)
projects.register("", ProjectsViewSet, "api-projects")

snapshots = routers.SimpleRouter(trailing_slash=False)
snapshots.register("", SnapshotsViewSet, "api-snapshots")

projects_urls = [
    path("", include(projects.urls)),
    path("<int:pk>/events/", EventListView.as_view(), name="api-events-list"),
    path("<int:pk>/snapshots/", include(snapshots.urls)),
    # The following endpoints are not documented and reviewed
    # yet.
    path(
        "<int:pk>/item-create/",
        DiskItemCreateView.as_view(),
        name="api_project_item_create",
    ),
    path(
        "<int:pk>/item-move/", DiskItemMoveView.as_view(), name="api_project_item_move"
    ),
    path(
        "<int:pk>/item-remove/",
        DiskItemRemoveView.as_view(),
        name="api_project_item_remove",
    ),
    path(
        "<int:pk>/item-publish/",
        ItemPublishView.as_view(),
        name="api_project_item_publish",
    ),
    path("<int:pk>/sources/link", SourceLinkView.as_view(), name="api_sources_link"),
    path(
        "published-items/<int:pk>/delete/",
        PublishedItemDeleteView.as_view(),
        name="api_published_item_delete",
    ),
]
