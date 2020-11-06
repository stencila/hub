from django.urls import re_path

from manager.api.routers import OptionalSlashRouter
from users.api.views.features import FeaturesView
from users.api.views.invites import InvitesViewSet
from users.api.views.tokens import TokensViewSet
from users.api.views.users import UsersViewSet

invites = OptionalSlashRouter()
invites.register("invites", InvitesViewSet, "api-invites")

tokens = OptionalSlashRouter()
tokens.register("tokens", TokensViewSet, "api-tokens")

users = OptionalSlashRouter()
users.register("users", UsersViewSet, "api-users")

urlpatterns = (
    [re_path(r"features/?", FeaturesView.as_view(), name="api-features")]
    + invites.urls
    + tokens.urls
    + users.urls
)
