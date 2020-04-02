from django.urls import path, re_path

from stencila_open.views import (
    OpenView,
    OpenDisplayView,
    OpenResultRawView,
    OpenFeedbackView,
    OpenMediaView,
    OpenPreviewView,
    OpenManifestView,
)

urlpatterns = [
    path("", OpenView.as_view(), name="open_main"),
    re_path("^(https?://.*)", OpenView.as_view(), name="open_main_with_url"),
    path("<slug:conversion_id>", OpenDisplayView.as_view(), name="open_result"),
    path(
        "<slug:conversion_id>/<slug:media_dir_id>.media/<filename>",
        OpenMediaView.as_view(),
        name="open_media",
    ),
    path(
        "<slug:conversion_id>/preview", OpenPreviewView.as_view(), name="open_preview"
    ),
    path(
        "<slug:conversion_id>/raw", OpenResultRawView.as_view(), name="open_result_raw"
    ),
    path(
        "<slug:conversion_id>/feedback",
        OpenFeedbackView.as_view(),
        name="open_feedback",
    ),
    path(
        "<slug:conversion_id>/manifest",
        OpenManifestView.as_view(),
        name="open_manifest",
    ),
]
