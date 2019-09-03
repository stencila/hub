from django.urls import path

from open.views import OpenView

urlpatterns = [
    path('', OpenView.as_view())
]
