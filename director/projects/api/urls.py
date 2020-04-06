from django.urls import path
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
    SnapshotView,
    ProjectEventListView,
    AdminProjectEventListView,
)
from projects.api.views.nodes import NodesViewSet

projects_urls = [
    path("", ProjectListView.as_view(), name="api_project_list"),
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
    path("<int:pk>/snapshot/", SnapshotView.as_view(), name="api_project_snapshot"),
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

nodes = routers.SimpleRouter()
nodes.register("", NodesViewSet, "api-nodes")
nodes_urls = format_suffix_patterns(nodes.urls)
