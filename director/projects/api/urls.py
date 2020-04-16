from django.urls import path, include

from general.api.routers import OptionalSlashRouter
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

nodes = OptionalSlashRouter()
nodes.register("nodes", NodesViewSet, "api-nodes")

projects = OptionalSlashRouter()
projects.register("projects", ProjectsViewSet, "api-projects")

snapshots = OptionalSlashRouter()
snapshots.register("snapshots", SnapshotsViewSet, "api-snapshots")

projects_urls = projects.urls + [
    path(
        "projects/",
        include(
            [
                # Nested routers
                path("<int:pk>/", include(snapshots.urls)),
                # Nested single views
                path(
                    "<int:pk>/events/", EventListView.as_view(), name="api-events-list"
                ),
                # The following endpoints are not documented and reviewed yet.
                path(
                    "<int:pk>/item-create/",
                    DiskItemCreateView.as_view(),
                    name="api_project_item_create",
                ),
                path(
                    "<int:pk>/item-move/",
                    DiskItemMoveView.as_view(),
                    name="api_project_item_move",
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
                path(
                    "<int:pk>/sources/link",
                    SourceLinkView.as_view(),
                    name="api_sources_link",
                ),
                path(
                    "published-items/<int:pk>/delete/",
                    PublishedItemDeleteView.as_view(),
                    name="api_published_item_delete",
                ),
            ]
        ),
    )
]
