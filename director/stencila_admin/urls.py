from django.urls import path
from .views import SessionStatusView


urlpatterns = [
    path('session-status/', SessionStatusView.as_view(), name='admin_session_status_list')
]
