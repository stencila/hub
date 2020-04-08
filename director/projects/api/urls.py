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
from projects.api.views.projects import (
    ProjectDetailView,
    ManifestView,
    ProjectListView,
    ProjectEventListView,
    AdminProjectEventListView,
)
from projects.api.views.nodes import NodesViewSet
from projects.api.views.snapshots import SnapshotsViewSet

snapshots = routers.SimpleRouter()
snapshots.register("", SnapshotsViewSet, "api-snapshots")
snapshots_urls = format_suffix_patterns(snapshots.urls)

nodes = routers.SimpleRouter()
nodes.register("", NodesViewSet, "api-nodes")
nodes_urls = format_suffix_patterns(nodes.urls)


projects_urls = [
    path("", ProjectListView.as_view(), name="api-projects-list"),
    path("<int:pk>/snapshots/", include(snapshots_urls)),
    # The following endpoints are not documented and reviewed
    # yet.
    path("<int:pk>", ProjectDetailView.as_view(), name="api_project_detail"),
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
    path("<int:pk>/manifest/", ManifestView.as_view(), name="api_project_manifest"),
    path(
        "<int:project_pk>/events/",
        ProjectEventListView.as_view(),
        name="api_project_event_list",
    ),
    path(
        "published-items/<int:pk>/delete/",
        PublishedItemDeleteView.as_view(),
        name="api_published_item_delete",
    ),
    path(
        "project-events/",
        AdminProjectEventListView.as_view(),
        name="api_admin_project_events",
    ),
]
