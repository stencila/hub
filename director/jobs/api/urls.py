from django.urls import path, include

from general.api.routers import OptionalSlashRouter
from jobs.api.views import (
    JobsViewSet,
    AccountsZonesViewSet,
    AccountsBrokerView,
    AccountsQueuesViewSet,
    AccountsWorkersViewSet,
    AccountsWorkersHeartbeatsViewSet,
    WorkersViewSet,
)

jobs = OptionalSlashRouter()
jobs.register("jobs", JobsViewSet, "api-jobs")

accounts_zones = OptionalSlashRouter()
accounts_zones.register("zones", AccountsZonesViewSet, "api-accounts-zones")

accounts_queues = OptionalSlashRouter()
accounts_queues.register("queues", AccountsQueuesViewSet, "api-accounts-queues")

accounts_workers = OptionalSlashRouter()
accounts_workers.register("workers", AccountsWorkersViewSet, "api-accounts-workers")

accounts_workers_heartbeats = OptionalSlashRouter()
accounts_workers_heartbeats.register(
    "heartbeats", AccountsWorkersHeartbeatsViewSet, "api-accounts-workers-heartbeats"
)

workers = OptionalSlashRouter()
workers.register("workers", WorkersViewSet, "api-workers")


urlpatterns = (
    jobs.urls
    + [
        path("accounts/<int:account>/broker", AccountsBrokerView.as_view()),
        path("accounts/<int:account>/", include(accounts_zones.urls)),
        path("accounts/<int:account>/", include(accounts_queues.urls)),
        path("accounts/<int:account>/", include(accounts_workers.urls)),
        path(
            "accounts/<int:account>/workers/<int:worker>/",
            include(accounts_workers_heartbeats.urls),
        ),
    ]
    + workers.urls
)
