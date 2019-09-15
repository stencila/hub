from django.urls import path, re_path

from stencila_open.views import OpenView, OpenResultView, OpenResultRawView, OpenFeedbackView, OpenMediaView

urlpatterns = [
    path('', OpenView.as_view(), name='open_main'),
    re_path('^(https?://.*)', OpenView.as_view(), name='open_main_with_url'),
    path('<slug:conversion_id>', OpenResultView.as_view(), name='open_result'),
    path('<slug:conversion_id>/<slug:media_dir_id>.media/<filename>', OpenMediaView.as_view(), name='open_media'),
    path('<slug:conversion_id>/raw', OpenResultRawView.as_view(), name='open_result_raw'),
    path('<slug:conversion_id>/feedback', OpenFeedbackView.as_view(), name='open_feedback')
]
