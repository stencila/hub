from general.api.routers import OptionalSlashRouter
from users.api.views.tokens import TokensViewSet
from users.api.views.users import UsersViewSet

tokens = OptionalSlashRouter()
tokens.register("tokens", TokensViewSet, "api-tokens")

users = OptionalSlashRouter()
users.register("users", UsersViewSet, "api-users")
