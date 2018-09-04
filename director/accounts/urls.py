from django.urls import path

from accounts.views import (
    AccountListView, AccountProfileView, AccountAccessView, AccountTeamsView, AccountSettingsView
)

urlpatterns = [
    path('', AccountListView.as_view(), name="account_list"),
    path('<int:pk>/', AccountProfileView.as_view(), name="account_profile"),
    path('<int:pk>/members/', AccountAccessView.as_view(), name="account_access"),
    path('<int:pk>/teams/',   AccountTeamsView.as_view(), name="account_teams"),
    path('<int:pk>/settings/', AccountSettingsView.as_view(), name="account_settings")
]
