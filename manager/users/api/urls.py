from manager.api.routers import OptionalSlashRouter
from users.api.views.invites import InvitesViewSet
from users.api.views.tokens import TokensViewSet
from users.api.views.users import UsersViewSet

invites = OptionalSlashRouter()
invites.register("invites", InvitesViewSet, "api-invites")

tokens = OptionalSlashRouter()
tokens.register("tokens", TokensViewSet, "api-tokens")

users = OptionalSlashRouter()
users.register("users", UsersViewSet, "api-users")

urlpatterns = invites.urls + tokens.urls + users.urls
