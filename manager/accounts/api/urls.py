from django.urls import include, path

from accounts.api.views import (
    AccountsTeamsMembersViewSet,
    AccountsTeamsViewSet,
    AccountsUsersViewSet,
    AccountsViewSet,
)
from manager.api.routers import OptionalSlashRouter

accounts = OptionalSlashRouter()
accounts.register("accounts", AccountsViewSet, "api-accounts")

accounts_users = OptionalSlashRouter()
accounts_users.register("users", AccountsUsersViewSet, "api-accounts-users")

accounts_teams = OptionalSlashRouter()
accounts_teams.register("teams", AccountsTeamsViewSet, "api-accounts-teams")

accounts_teams_members = OptionalSlashRouter()
accounts_teams_members.register(
    "members", AccountsTeamsMembersViewSet, "api-accounts-teams-members"
)

urlpatterns = accounts.urls + [
    path("accounts/<account>/", include(accounts_users.urls)),
    path("accounts/<account>/", include(accounts_teams.urls)),
    path("accounts/<account>/teams/<team>/", include(accounts_teams_members.urls)),
]
