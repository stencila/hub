from django.urls import include, path

from accounts.api.views import AccountsViewSet, TeamsViewSet
from manager.api.routers import OptionalSlashRouter

accounts = OptionalSlashRouter()
accounts.register("accounts", AccountsViewSet, "api-accounts")

accounts_teams = OptionalSlashRouter()
accounts_teams.register("teams", TeamsViewSet, "api-accounts-teams")

urlpatterns = accounts.urls + [
    path("accounts/<str:account>/", include(accounts_teams.urls)),
]
