from accounts.api.views import AccountsViewSet
from manager.api.routers import OptionalSlashRouter

accounts = OptionalSlashRouter()
accounts.register("accounts", AccountsViewSet, "api-accounts")
