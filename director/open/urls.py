from django.urls import path

from open.views import OpenView, OpenResultView, OpenResultRawView

urlpatterns = [
    path('', OpenView.as_view(), name='open_main'),
    path('<slug:conversion_id>', OpenResultView.as_view(), name='open_result'),
    path('<slug:conversion_id>/raw', OpenResultRawView.as_view(), name='open_result_raw'),
]
