from django.urls import path

from accounts.views import (
    AccountListView, AccountProfileView, AccountAccessView, AccountSettingsView, TeamDetailView, TeamListView,
    TeamMembersView
)

urlpatterns = [
    path('', AccountListView.as_view(), name="account_list"),
    path('<int:pk>/', AccountProfileView.as_view(), name="account_profile"),
    path('<int:pk>/members/', AccountAccessView.as_view(), name="account_access"),
    path('<int:pk>/settings/', AccountSettingsView.as_view(), name="account_settings"),
    path('<int:account_pk>/teams/create', TeamDetailView.as_view(), name="account_team_create"),
    path('<int:account_pk>/teams/<int:team_pk>', TeamDetailView.as_view(), name="account_team_detail"),
    path('<int:account_pk>/teams/<int:team_pk>/members', TeamMembersView.as_view(), name="account_team_members"),
    path('<int:account_pk>/teams', TeamListView.as_view(), name="account_team_list")
]
