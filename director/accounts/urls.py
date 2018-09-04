from django.urls import path

from accounts.views import (
    AccountProfileView, AccountAccessView, AccountTeamsView, AccountSettingsView
)

urlpatterns = [
    path('<int:pk>/', AccountProfileView.as_view(), name="account_profile"),
    path('<int:pk>/members/', AccountAccessView.as_view(), name="account_access"),
    path('<int:pk>/teams/',   AccountTeamsView.as_view(), name="account_teams"),
    path('<int:pk>/settings/', AccountSettingsView.as_view(), name="account_settings")
]
