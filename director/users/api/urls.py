from rest_framework import routers

from users.api.views.tokens import TokensViewSet
from users.api.views.users import UsersViewSet

tokens = routers.SimpleRouter()
tokens.register("", TokensViewSet, "api-tokens")

users = routers.SimpleRouter()
users.register("", UsersViewSet, "api-users")
