from django.urls import path

from projects.views.source_api_views import DiskItemCreateView, DiskItemMoveView, DiskItemRemoveView, SourceLinkView, \
    ItemPublishView, PublishedItemDeleteView
from projects.views.project_api_views import ProjectDetailView, ManifestView, ProjectListView, SnapshotView, \
    ProjectEventListView

urlpatterns = [
    path('', ProjectListView.as_view(), name='api_v1_project_list'),
    path('<int:pk>', ProjectDetailView.as_view(), name='api_v1_project_detail'),
    path('<int:pk>/item-create/', DiskItemCreateView.as_view(), name='api_v1_project_item_create'),
    path('<int:pk>/item-move/', DiskItemMoveView.as_view(), name='api_v1_project_item_move'),
    path('<int:pk>/item-remove/', DiskItemRemoveView.as_view(), name='api_v1_project_item_remove'),
    path('<int:pk>/item-publish/', ItemPublishView.as_view(), name='api_v1_project_item_publish'),
    path('<int:pk>/sources/link', SourceLinkView.as_view(), name='api_v1_sources_link'),
    path('<int:pk>/manifest/', ManifestView.as_view(), name='api_v1_project_manifest'),
    path('<int:pk>/snapshot/', SnapshotView.as_view(), name='api_v1_project_snapshot'),
    path('<int:project_pk>/events/', ProjectEventListView.as_view(), name='api_v1_project_event_list'),
    path('published-items/<int:pk>/delete/', PublishedItemDeleteView.as_view(), name='api_v1_published_item_delete')
]
