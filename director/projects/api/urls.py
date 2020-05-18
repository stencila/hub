from django.urls import path, include

from general.api.routers import OptionalSlashRouter
from projects.api.views.sources import (
    ProjectsSourcesViewSet,
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

projects_sources = OptionalSlashRouter()
projects_sources.register("sources", ProjectsSourcesViewSet, "api-files")

projects_snapshots = OptionalSlashRouter()
projects_snapshots.register("snapshots", SnapshotsViewSet, "api-snapshots")

urlpatterns = projects.urls + [
    # Nested routers
    path("projects/<int:project>/", include(projects_sources.urls)),
    path("projects/<int:pk>/", include(projects_snapshots.urls)),
    # Internal API endpoints; not documented and reviewed yet.
    path(
        "projects/",
        include(
            [
                path(
                    "<int:pk>/events/", EventListView.as_view(), name="api-events-list"
                ),
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
    ),
]
