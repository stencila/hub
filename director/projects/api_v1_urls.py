from django.urls import path

from projects.source_api_views import DiskItemCreateView, DiskItemMoveView, DiskItemRemoveView

urlpatterns = [
    path('<int:pk>/item-create', DiskItemCreateView.as_view(), name='api_v1_project_item_create'),
    path('<int:pk>/item-move', DiskItemMoveView.as_view(), name='api_v1_project_item_move'),
    path('<int:pk>/item-remove', DiskItemRemoveView.as_view(), name='api_v1_project_item_remove')
]
